# src/core/integrations/openai/base_client.py

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional, Union

import aiohttp
import sentry_sdk
from core.config.config import OpenAIServiceAccount, settings
from core.metrics.metrics import REQUEST_COUNT, REQUEST_LATENCY, TOKEN_USAGE
from core.utils.logger import get_logger
from pydantic import ValidationError

from .types import (
    APIError,
    AuthenticationError,
    OpenAIError,
    OpenAIErrorResponse,
    OpenAIResponse,
    RateLimitError,
    StreamEvent,
)

logger = get_logger(__name__)


class OpenAIBaseClient:
    """Base client for OpenAI API interactions."""

    def __init__(self, service_account: OpenAIServiceAccount):
        """
        Initialize the base client with a specific OpenAI service account.

        Args:
            service_account (OpenAIServiceAccount): The service account to use for API interactions.
        """
        self.service_account = service_account
        self.config = self.service_account
        self.logger = logger
        self.headers = {
            "Authorization": f"Bearer {self.service_account.api_secret_key.get_secret_value()}",
            "Content-Type": "application/json",
            "OpenAI-Organization": self.service_account.organization_id or "",
            "OpenAI-Assistants": "assistants=v2",  # Custom header if required
        }
        self.api_url = self.config.base_url or "https://api.openai.com/v1"
        self.max_retries = self.config.max_retries
        self.backoff_factor = self.config.backoff_factor
        self.backoff_strategy = self.config.backoff_strategy
        self.timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        self.stream_timeout = aiohttp.ClientTimeout(
            total=(self.config.streaming.timeout if self.config.streaming else 120)
        )
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self.logger.info("Created new aiohttp ClientSession")
        return self._session

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        stream: bool = False,
        cancel_event: Optional[asyncio.Event] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[StreamEvent]]:
        """
        Make an HTTP request to the OpenAI API with retry logic and error handling.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST').
            endpoint (str): API endpoint (e.g., 'assistants').
            data (Optional[Dict]): JSON payload for the request.
            params (Optional[Dict]): Query parameters for the request.
            stream (bool): Whether to handle the response as a stream.
            cancel_event (Optional[asyncio.Event]): Event to signal cancellation of streaming.

        Returns:
            Union[Dict[str, Any], AsyncIterator[StreamEvent]]: Parsed JSON response or an async generator for streaming.
        """
        url = f"{self.api_url}/{endpoint}"
        retry_count = 0
        request_id = str(uuid.uuid4())  # Unique identifier for each request
        start_time = time.time()

        while retry_count <= self.max_retries:
            try:
                session = await self._get_session()
                request_timeout = self.stream_timeout if stream else self.timeout
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self.headers,
                    timeout=request_timeout,
                ) as response:
                    latency = time.time() - start_time
                    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)

                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 1))
                        self.logger.warning(
                            f"[{request_id}] Rate limit hit. Retrying after {retry_after} seconds."
                        )
                        REQUEST_COUNT.labels(endpoint=endpoint, status="429").inc()
                        await asyncio.sleep(retry_after)
                        retry_count += 1
                        continue

                    if 500 <= response.status < 600:
                        self.logger.warning(
                            f"[{request_id}] Server error {response.status}. Retrying..."
                        )
                        REQUEST_COUNT.labels(
                            endpoint=endpoint, status=str(response.status)
                        ).inc()
                        await self._apply_backoff(retry_count)
                        retry_count += 1
                        continue

                    if stream and response.status == 200:
                        self.logger.info(
                            f"[{request_id}] Handling streaming response for {endpoint}"
                        )
                        REQUEST_COUNT.labels(endpoint=endpoint, status="stream").inc()
                        return self._handle_stream(response, cancel_event, request_id)

                    if response.status not in (200, 201):
                        try:
                            error_text = await response.text()
                            error_data = json.loads(error_text)
                            error_model = OpenAIErrorResponse(**error_data)
                        except (json.JSONDecodeError, ValidationError):
                            error_data = {
                                "error": {"message": error_text or "Unknown error"}
                            }
                        self.logger.error(
                            f"[{request_id}] OpenAI API call failed: {response.status} - {error_data}"
                        )
                        REQUEST_COUNT.labels(
                            endpoint=endpoint, status=str(response.status)
                        ).inc()
                        self._handle_error(response.status, error_data)

                    # Parse successful response
                    response_data = await response.json()
                    try:
                        openai_response = OpenAIResponse(**response_data)
                    except ValidationError as ve:
                        self.logger.error(f"[{request_id}] Validation error: {ve}")
                        raise OpenAIError(f"Response validation failed: {ve}") from ve

                    self.logger.info(
                        f"[{request_id}] Successful {method} request to {endpoint}"
                    )
                    REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()

                    # Token usage tracking
                    if openai_response.usage:
                        usage = openai_response.usage
                        TOKEN_USAGE.labels(endpoint=endpoint).inc(usage.total_tokens)

                    return openai_response.dict()

            except aiohttp.ClientError as e:
                self.logger.warning(
                    f"[{request_id}] Client error: {str(e)}. Retrying..."
                )
                REQUEST_COUNT.labels(endpoint=endpoint, status="client_error").inc()
                await self._apply_backoff(retry_count)
                retry_count += 1
                continue
            except asyncio.TimeoutError:
                self.logger.warning(f"[{request_id}] Request timed out. Retrying...")
                REQUEST_COUNT.labels(endpoint=endpoint, status="timeout").inc()
                await self._apply_backoff(retry_count)
                retry_count += 1
                continue
            except OpenAIError as e:
                self.logger.exception(f"[{request_id}] OpenAI error: {e}")
                REQUEST_COUNT.labels(endpoint=endpoint, status="openai_error").inc()
                sentry_sdk.capture_exception(e)
                raise
            except Exception as e:
                self.logger.exception(
                    f"[{request_id}] An unexpected error occurred during OpenAI API call"
                )
                REQUEST_COUNT.labels(endpoint=endpoint, status="unexpected_error").inc()
                sentry_sdk.capture_exception(e)
                raise OpenAIError(f"Unexpected error: {str(e)}") from e

        self.logger.error(
            f"[{request_id}] Failed to make request to {endpoint} after {self.max_retries} retries."
        )
        REQUEST_COUNT.labels(endpoint=endpoint, status="failed").inc()
        sentry_sdk.capture_message(
            f"Request to {endpoint} failed after {self.max_retries} retries."
        )
        raise OpenAIError(
            f"Request to {endpoint} failed after {self.max_retries} retries."
        )

    async def _apply_backoff(self, retry_count: int):
        """
        Apply backoff delay based on the retry count and backoff strategy.

        Args:
            retry_count (int): The current retry attempt.
        """
        if self.backoff_strategy == "linear":
            delay = self.backoff_factor * retry_count
        elif self.backoff_strategy == "fixed":
            delay = self.backoff_factor
        else:  # Exponential
            delay = self.backoff_factor**retry_count
        self.logger.debug(f"Applying backoff: sleeping for {delay} seconds.")
        await asyncio.sleep(delay)

    async def _handle_stream(
        self,
        response: aiohttp.ClientResponse,
        cancel_event: Optional[asyncio.Event],
        request_id: str,
    ) -> AsyncIterator[StreamEvent]:
        """
        Handle streaming responses from the OpenAI API.

        Args:
            response (aiohttp.ClientResponse): The streaming response object.
            cancel_event (Optional[asyncio.Event]): Event to signal cancellation of streaming.
            request_id (str): Unique identifier for the request.

        Yields:
            StreamEvent: Parsed streaming event data.
        """
        async for line in response.content:
            if cancel_event and cancel_event.is_set():
                self.logger.info(f"[{request_id}] Streaming canceled by user.")
                break
            if line:
                decoded_line = line.decode("utf-8").strip()
                if decoded_line.startswith("data: "):
                    data = decoded_line.split("data: ", 1)[1]
                    if data == "[DONE]":
                        self.logger.info(f"[{request_id}] Stream ended with [DONE]")
                        break
                    try:
                        json_data = json.loads(data)
                        stream_event = StreamEvent(
                            type=json_data.get("object", ""),
                            data=json_data,
                            id=json_data.get("id"),
                            created_at=datetime.fromtimestamp(
                                json_data.get("created", 0)
                            ),
                        )
                        yield stream_event
                    except json.JSONDecodeError as e:
                        self.logger.error(
                            f"[{request_id}] Failed to parse stream data: {str(e)}"
                        )
                        sentry_sdk.capture_exception(e)

    def _handle_error(self, status_code: int, response_data: Dict):
        """
        Handle API errors by raising appropriate exceptions.

        Args:
            status_code (int): HTTP status code.
            response_data (Dict): Parsed JSON response data.

        Raises:
            RateLimitError: If rate limit is exceeded.
            AuthenticationError: If authentication fails.
            APIError: For other API-related errors.
        """
        error_msg = response_data.get("error", {}).get("message", "Unknown error")

        if status_code == 429:
            sentry_sdk.capture_message(f"Rate limit exceeded: {error_msg}")
            raise RateLimitError(error_msg)
        elif status_code == 401:
            sentry_sdk.capture_message(f"Authentication failed: {error_msg}")
            raise AuthenticationError(error_msg)
        elif status_code == 400:
            sentry_sdk.capture_message(f"Bad Request: {error_msg}")
            raise APIError(f"Bad Request: {error_msg}", status_code)
        elif status_code == 404:
            sentry_sdk.capture_message(f"Not Found: {error_msg}")
            raise APIError(f"Not Found: {error_msg}", status_code)
        else:
            sentry_sdk.capture_message(f"API Error ({status_code}): {error_msg}")
            raise APIError(error_msg, status_code)

    async def close(self):
        """Closes the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self.logger.info("Closed aiohttp ClientSession")
