# src/core/integrations/openai/config.py

import asyncio
import logging
import os  # For environment variable access
from typing import Any, Dict, List, Optional

import openai
import sentry_sdk
from prometheus_client import Counter, Histogram
from pydantic import BaseModel, Field, SecretStr, validator

from zimbot.core.config.config import (  # Import centralized models and SecretsConfig
    OpenAIServiceAccount,
    SecretsConfig,
    settings,
)

# Initialize Sentry
sentry_sdk.init(
    dsn=settings.sentry_dsn.get_secret_value(),  # Correct DSN source
    traces_sample_rate=1.0,
    environment=settings.app_env,
)

logger = logging.getLogger(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "openai_requests_total", "Total number of OpenAI API requests", ["model"]
)
REQUEST_LATENCY = Histogram(
    "openai_request_latency_seconds",
    "Latency of OpenAI API requests",
    ["model"],
)
TOKEN_USAGE = Counter(
    "openai_tokens_used_total",
    "Total tokens used in OpenAI API requests",
    ["model"],
)


class StreamingConfig(BaseModel):
    """Configuration specific to streaming responses from OpenAI."""

    timeout: int = Field(
        120,
        ge=1,
        description="Timeout in seconds for streaming responses from OpenAI API.",
    )
    max_chunk_size: Optional[int] = Field(
        None, description="Maximum size for streamed chunks in bytes."
    )


class ModelRegistry:
    """Dynamic registry to manage and prioritize OpenAI models."""

    def __init__(self, service_account: OpenAIServiceAccount):
        self.service_account = service_account
        self.acceptable_versions = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ]
        self.model_priority = {
            model: idx for idx, model in enumerate(self.acceptable_versions)
        }

    def get_priority(self, model: str) -> int:
        return self.model_priority.get(model, len(self.acceptable_versions))

    async def fetch_available_models(self) -> List[str]:
        """Fetch available models from OpenAI API."""
        try:
            response = await openai.Model.list()
            available_models = [model["id"] for model in response["data"]]
            logger.info(f"Fetched available models: {available_models}")
            return available_models
        except Exception as e:
            logger.error(f"Failed to fetch available models: {e}")
            sentry_sdk.capture_exception(e)
            return []

    async def get_best_available_model(
        self, available_models: List[str]
    ) -> Optional[str]:
        """Return the highest priority model available."""
        available_models_sorted = sorted(
            [model for model in available_models if model in self.acceptable_versions],
            key=lambda m: self.get_priority(m),
        )
        for model in available_models_sorted:
            if self.get_priority(model) <= self.get_priority(
                self.service_account.min_model_version
            ):
                return model
        return None


class BatchRequestHandler:
    """Handles batch requests to OpenAI API where supported."""

    def __init__(self, client: "OpenAIClient"):
        self.client = client
        self.semaphore = asyncio.Semaphore(10)  # Adjust concurrency as needed

    async def create_completions_batch(
        self, requests: List[Dict[str, Any]]
    ) -> List[Any]:
        """Create a batch of completions with enhanced logging and metrics tracking."""
        results = []

        async def fetch(request: Dict[str, Any], index: int):
            async with self.semaphore:
                try:
                    result = await self.client.create_completion(**request)
                    logger.info(f"Batch request {index} succeeded.")
                    REQUEST_COUNT.labels(model=request.get("model")).inc()
                    token_usage = result["usage"]["total_tokens"]
                    TOKEN_USAGE.labels(model=request.get("model")).inc(token_usage)
                    return result
                except Exception as e:
                    logger.error(f"Batch request {index} failed: {e}")
                    sentry_sdk.capture_exception(e)
                    return None

        tasks = [
            asyncio.create_task(fetch(req, idx))
            for idx, req in enumerate(requests, start=1)
        ]
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
        return results


class OpenAIClient:
    """Client to interact with OpenAI API based on service account configuration."""

    def __init__(self, service_account: OpenAIServiceAccount):
        self.service_account = service_account
        self.available_models = []
        self.model_registry = ModelRegistry(service_account)
        self.batch_handler = BatchRequestHandler(self)
        self.default_model = service_account.default_model
        self.backup_model = service_account.backup_model
        self.min_model_version = service_account.min_model_version
        self.max_retries = service_account.max_retries
        self.backoff_factor = service_account.backoff_factor
        self.backoff_strategy = service_account.backoff_strategy
        self.request_timeout = service_account.request_timeout
        self.streaming_config = service_account.streaming

        # Initialize secrets and models
        asyncio.create_task(self.initialize_secrets())
        asyncio.create_task(self.update_available_models())

    async def initialize_secrets(self):
        """Initialize secrets using SecretsConfig."""
        self.api_key = await SecretsConfig.get_secret(
            f"OPENAI_API_SECRET_KEY{self.service_account.index}"
        )
        if self.service_account.organization_id:
            self.organization_id = await SecretsConfig.get_secret(
                f"OPENAI_ORGANIZATION_ID{self.service_account.index}"
            )
        # Configure OpenAI client with fetched secrets
        openai.api_key = self.api_key
        openai.api_base = self.service_account.base_url
        if self.service_account.organization_id:
            openai.organization = self.organization_id

    async def update_available_models(self):
        """Periodically update the list of available models."""
        while True:
            self.available_models = await self.model_registry.fetch_available_models()
            logger.info(f"Updated available models: {self.available_models}")
            await asyncio.sleep(3600)  # Update every hour

    def get_model(self) -> str:
        """Return the current model to use, ensuring it meets the minimum version requirement."""
        # Run coroutine in the current event loop to get the best available model
        loop = asyncio.get_event_loop()
        selected_model = loop.run_until_complete(
            self.model_registry.get_best_available_model(self.available_models)
        )
        if selected_model:
            return selected_model
        else:
            logger.warning(
                f"No acceptable models available above {self.min_model_version}. Falling back to min_model_version."
            )
            return self.min_model_version

    def switch_model(self):
        """Switch to the backup model."""
        logger.info(f"Switching model from {self.default_model} to {self.backup_model}")
        self.default_model, self.backup_model = (
            self.backup_model,
            self.default_model,
        )

    async def create_completion(self, **kwargs) -> Any:
        """Create a completion with retry logic and metrics tracking."""
        model = self.get_model()
        retries = 0
        while retries <= self.max_retries:
            with REQUEST_LATENCY.labels(model=model).time():
                try:
                    response = await openai.ChatCompletion.acreate(
                        model=model,
                        **kwargs,
                        timeout=self.request_timeout,
                    )
                    # Update token usage
                    token_usage = response["usage"]["total_tokens"]
                    TOKEN_USAGE.labels(model=model).inc(token_usage)
                    REQUEST_COUNT.labels(model=model).inc()
                    return response
                except openai.error.RateLimitError as e:
                    logger.warning(
                        f"Rate limit exceeded. Retrying after backoff. Retry {retries + 1}/{self.max_retries}"
                    )
                    sentry_sdk.capture_exception(e)
                    await asyncio.sleep(
                        self.backoff_factor * (2**retries)
                        if self.backoff_strategy == "exponential"
                        else self.backoff_factor * (retries + 1)
                    )
                    retries += 1
                    if retries > self.max_retries:
                        logger.error(
                            "Max retries exceeded for RateLimitError. Switching model."
                        )
                        self.switch_model()
                        raise
                except openai.error.Timeout as e:
                    logger.warning(
                        f"Request timed out. Retrying after backoff. Retry {retries + 1}/{self.max_retries}"
                    )
                    sentry_sdk.capture_exception(e)
                    await asyncio.sleep(
                        self.backoff_factor * (2**retries)
                        if self.backoff_strategy == "exponential"
                        else self.backoff_factor * (retries + 1)
                    )
                    retries += 1
                    if retries > self.max_retries:
                        logger.error(
                            "Max retries exceeded for TimeoutError. Switching model."
                        )
                        self.switch_model()
                        raise
                except Exception as e:
                    logger.error(
                        f"Unexpected error during OpenAI request: {e}. Switching model."
                    )
                    sentry_sdk.capture_exception(e)
                    self.switch_model()
                    raise

    async def stream_completion(self, **kwargs) -> Any:
        """Stream completion responses with timeout management."""
        model = self.get_model()
        try:
            async for chunk in openai.ChatCompletion.acreate(
                model=model,
                stream=True,
                **kwargs,
                timeout=(
                    self.streaming_config.timeout
                    if self.streaming_config
                    else self.request_timeout
                ),
            ):
                yield chunk
        except openai.error.RateLimitError as e:
            logger.warning(
                f"RateLimitError during streaming: {e}. Switching model and retrying."
            )
            sentry_sdk.capture_exception(e)
            self.switch_model()
            raise
        except openai.error.Timeout as e:
            logger.error(f"TimeoutError during streaming: {e}. Switching model.")
            sentry_sdk.capture_exception(e)
            self.switch_model()
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during streaming completion: {e}. Switching model."
            )
            sentry_sdk.capture_exception(e)
            self.switch_model()
            raise


class OpenAIServiceManager:
    """Manager to handle multiple OpenAI service accounts."""

    def __init__(self, service_accounts: List[OpenAIServiceAccount]):
        if not service_accounts:
            raise ValueError("At least one OpenAI service account must be provided.")
        self.clients = [OpenAIClient(account) for account in service_accounts]
        self.current_client_index = 0
        self.total_clients = len(self.clients)
        self.lock = asyncio.Lock()

    def get_current_client(self) -> OpenAIClient:
        """Get the current OpenAI client."""
        return self.clients[self.current_client_index]

    async def switch_to_next_client(self):
        """Switch to the next OpenAI client in the list."""
        async with self.lock:
            self.current_client_index = (
                self.current_client_index + 1
            ) % self.total_clients
            logger.info(
                f"Switched to OpenAI client {self.current_client_index + 1}/{self.total_clients}"
            )

    async def create_completion(self, **kwargs) -> Any:
        """Create a completion using the current client, with fallback to backup clients if needed."""
        client = self.get_current_client()
        try:
            return await client.create_completion(**kwargs)
        except (openai.error.RateLimitError, openai.error.Timeout) as e:
            logger.error(
                f"Error with OpenAI client {self.current_client_index + 1}: {e}. Attempting to switch client."
            )
            sentry_sdk.capture_exception(e)
            await self.switch_to_next_client()
            if self.total_clients > 1:
                return await self.create_completion(**kwargs)
            else:
                raise
        except Exception as e:
            logger.error(
                f"Unexpected error with OpenAI client {self.current_client_index + 1}: {e}."
            )
            sentry_sdk.capture_exception(e)
            raise

    async def stream_completion(self, **kwargs) -> Any:
        """Stream completion using the current client, with fallback to backup clients if needed."""
        client = self.get_current_client()
        try:
            async for chunk in client.stream_completion(**kwargs):
                yield chunk
        except (openai.error.RateLimitError, openai.error.Timeout) as e:
            logger.error(
                f"Error with OpenAI client {self.current_client_index + 1} during streaming: {e}. Attempting to switch client."
            )
            sentry_sdk.capture_exception(e)
            await self.switch_to_next_client()
            if self.total_clients > 1:
                async for chunk in self.stream_completion(**kwargs):
                    yield chunk
            else:
                raise
        except Exception as e:
            logger.error(
                f"Unexpected error during streaming with OpenAI client {self.current_client_index + 1}: {e}."
            )
            sentry_sdk.capture_exception(e)
            raise


# Instantiate OpenAIServiceManager with service accounts from main config
openai_service_manager = OpenAIServiceManager(settings.openai.service_accounts)
