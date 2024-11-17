# src/core/secrets/secrets_retriever.py

"""
Module for retrieving secrets from AWS Secrets Manager.
Handles parsing, retry logic with exponential backoff, and enhanced alerting mechanisms.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import sentry_sdk
from botocore.exceptions import ClientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .alerting import Alerting
from .aws_client_manager import AWSSecretsClientManager
from .caching import Caching
from .circuit_breaker import CircuitBreakerManager, with_circuit_breaker
from .error_handling import handle_error
from .exceptions import CachingError, MaxRetriesExceededError, MissingSecretError
from .metrics import Metrics
from .metrics_decorators import (
    measure_latency_async_with_metrics,
    measure_latency_sync_with_metrics,
)
from .secrets_config import SecretsManagerConfig

logger = logging.getLogger(__name__)


class SecretsRetriever:
    """
    Handles the retrieval of secrets from AWS Secrets Manager.
    """

    def __init__(
        self,
        aws_client_manager: AWSSecretsClientManager,
        caching: Caching,
        alerting: Alerting,
        metrics: Metrics,
        config: SecretsManagerConfig,
        circuit_breaker_manager: CircuitBreakerManager,
    ):
        """
        Initialize the SecretsRetriever.

        Args:
            aws_client_manager (AWSSecretsClientManager): Manager for AWS clients.
            caching (Caching): Cache manager for secrets.
            alerting (Alerting): Alerting utility for sending alerts.
            metrics (Metrics): Metrics utility for tracking performance.
            config (SecretsManagerConfig): Centralized configuration.
            circuit_breaker_manager (CircuitBreakerManager): Manager for circuit breakers.
        """
        self.aws_client_manager = aws_client_manager
        self.caching = caching
        self.alerting = alerting
        self.metrics = metrics
        self.config = config
        self.circuit_breaker_manager = circuit_breaker_manager

    @measure_latency_async_with_metrics
    @retry(
        wait=wait_exponential(
            multiplier=self.config.backoff_base,
            min=self.config.backoff_base,
            max=self.config.backoff_base * 10,
        ),
        stop=stop_after_attempt(self.config.max_retries),
        retry=retry_if_exception_type((ClientError, CachingError)),
        reraise=True,
    )
    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_aws_circuit_breaker()
    )
    async def get_secret_async(self, secret_name: str) -> str:
        """
        Asynchronously retrieve a secret, utilizing caching and retry logic.
        """
        # Attempt to retrieve from cache
        secret = await self.caching.get_cached_secret(secret_name)
        if secret:
            self.metrics.cache_hit_counter.labels(cache_type="async").inc()
            logger.debug(f"Async cache hit for secret '{secret_name}'")
            return secret
        else:
            self.metrics.cache_miss_counter.labels(cache_type="async").inc()
            logger.debug(f"Async cache miss for secret '{secret_name}'")

        try:
            secret_value = await self.aws_client_manager.fetch_secret_async(secret_name)
            await self.caching.set_cached_secret(secret_name, secret_value)
            return secret_value
        except ClientError as e:
            await self._handle_client_error_async(e, secret_name)
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
            metadata = self._build_metadata(secret_name, e)
            await self.alerting.send_alert(
                f"Failed to retrieve secret '{secret_name}': {e}", metadata
            )
            raise MaxRetriesExceededError(
                f"Failed to retrieve secret '{secret_name}' after {self.config.max_retries} attempts."
            ) from e

    @measure_latency_sync_with_metrics
    @retry(
        wait=wait_exponential(
            multiplier=self.config.backoff_base,
            min=self.config.backoff_base,
            max=self.config.backoff_base * 10,
        ),
        stop=stop_after_attempt(self.config.max_retries),
        retry=retry_if_exception_type((ClientError, CachingError)),
        reraise=True,
    )
    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_aws_circuit_breaker()
    )
    def get_secret_sync(self, secret_name: str) -> str:
        """
        Synchronously retrieve a secret with caching and retry logic.
        """
        secret = self.caching.get_cached_secret(secret_name)
        if secret:
            self.metrics.cache_hit_counter.labels(cache_type="sync").inc()
            logger.debug(f"Sync cache hit for secret '{secret_name}'")
            return secret

        self.metrics.cache_miss_counter.labels(cache_type="sync").inc()
        logger.debug(f"Sync cache miss for secret '{secret_name}'")

        try:
            secret_value = self.aws_client_manager.fetch_secret_sync(secret_name)
            asyncio.run(self.caching.set_cached_secret(secret_name, secret_value))
            return secret_value
        except ClientError as e:
            self._handle_client_error_sync(e, secret_name)
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
            metadata = self._build_metadata(secret_name, e)
            self.alerting.send_alert(
                f"Failed to retrieve secret '{secret_name}': {e}", metadata
            )
            raise MaxRetriesExceededError(
                f"Failed to retrieve secret '{secret_name}' after {self.config.max_retries} attempts."
            ) from e

    def _parse_secret_response(self, response: Dict[str, Any], secret_name: str) -> str:
        """
        Parse the AWS Secrets Manager response to extract the secret.

        Args:
            response (Dict[str, Any]): AWS Secrets Manager response.
            secret_name (str): The name of the secret being retrieved.

        Returns:
            str: The secret value.

        Raises:
            MissingSecretError: If the secret is not found in the response.
            ValueError: If the secret format is invalid.
        """
        secret = response.get("SecretString") or response.get("SecretBinary")
        if secret is None:
            logger.error(f"Secret '{secret_name}' has no SecretString or SecretBinary.")
            raise ValueError(
                f"Secret '{secret_name}' has no SecretString or SecretBinary."
            )

        # Convert binary secret to string if necessary
        if isinstance(secret, bytes):
            secret = secret.decode("utf-8")
            logger.debug(f"Converted binary secret '{secret_name}' to string.")

        try:
            secret_dict = json.loads(secret)
            logger.debug(f"Parsed JSON for secret '{secret_name}'.")
        except json.JSONDecodeError as jde:
            logger.error(f"Invalid JSON format for secret '{secret_name}': {jde}")
            sentry_sdk.capture_exception(jde)
            raise ValueError(
                f"Invalid JSON format for secret '{secret_name}'."
            ) from jde

        secret_value = secret_dict.get(secret_name)
        if secret_value is None:
            logger.error(
                f"Secret key '{secret_name}' not found in AWS Secrets Manager response."
            )
            raise MissingSecretError(secret_name)

        return secret_value

    async def refresh_secret_async(self, secret_name: str) -> str:
        """
        Asynchronously refresh a specific secret by clearing its cache and re-fetching it.

        Args:
            secret_name (str): The name of the secret to refresh.

        Returns:
            str: The refreshed secret value.
        """
        logger.debug(f"Refreshing secret '{secret_name}' asynchronously.")
        await self.caching.remove_cached_secret(secret_name)
        return await self.get_secret_async(secret_name)

    def refresh_secret_sync(self, secret_name: str) -> str:
        """
        Synchronously refresh a specific secret by clearing its cache and re-fetching it.

        Args:
            secret_name (str): The name of the secret to refresh.

        Returns:
            str: The refreshed secret value.
        """
        logger.debug(f"Refreshing secret '{secret_name}' synchronously.")
        self.caching.remove_cached_secret(secret_name)
        return self.get_secret_sync(secret_name)

    async def refresh_all_secrets_async(
        self, secret_names: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Asynchronously refresh multiple secrets by clearing their cache and re-fetching them.

        Args:
            secret_names (List[str]): List of secret names to refresh.

        Returns:
            Dict[str, Optional[str]]: Dictionary mapping secret names to their refreshed values.
        """
        logger.debug(f"Refreshing all secrets asynchronously: {secret_names}")
        tasks = [self.refresh_secret_async(name) for name in secret_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        refreshed_secrets = {}
        for name, result in zip(secret_names, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to refresh secret '{name}': {result}")
                metadata = self._build_metadata(name, result)
                await self.alerting.send_alert(
                    f"Failed to refresh secret '{name}': {result}", metadata
                )
                refreshed_secrets[name] = None
            else:
                refreshed_secrets[name] = result
        return refreshed_secrets

    def refresh_all_secrets_sync(
        self, secret_names: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Synchronously refresh multiple secrets by clearing their cache and re-fetching them.

        Args:
            secret_names (List[str]): List of secret names to refresh.

        Returns:
            Dict[str, Optional[str]]: Dictionary mapping secret names to their refreshed values.
        """
        logger.debug(f"Refreshing all secrets synchronously: {secret_names}")
        refreshed_secrets = {}
        for name in secret_names:
            try:
                refreshed_secrets[name] = self.refresh_secret_sync(name)
            except Exception as e:
                logger.error(f"Failed to refresh secret '{name}': {e}")
                metadata = self._build_metadata(name, e)
                self.alerting.send_alert(
                    f"Failed to refresh secret '{name}': {e}", metadata
                )
                refreshed_secrets[name] = None
        return refreshed_secrets

    def _handle_client_error_sync(self, error: ClientError, secret_name: str):
        """
        Handle AWS ClientError exceptions with additional context in sync mode.

        Args:
            error (ClientError): The exception raised by AWS SDK.
            secret_name (str): The name of the secret being retrieved.

        Raises:
            MissingSecretError: If the error code is 'ResourceNotFoundException'.
            MaxRetriesExceededError: For all other AWS ClientErrors after retries.
        """
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        metadata = self._build_metadata(secret_name, error, error_code=error_code)
        alert_message = f"Error retrieving secret '{secret_name}': {error_code}"

        handle_error(error, alert_message, logger, self.alerting, metadata)
        if error_code == "ResourceNotFoundException":
            raise MissingSecretError(secret_name)
        else:
            raise MaxRetriesExceededError(
                f"Failed to retrieve secret '{secret_name}' after {self.config.max_retries} attempts."
            ) from error

    async def _handle_client_error_async(self, error: ClientError, secret_name: str):
        """
        Handle AWS ClientError exceptions with additional context in async mode.

        Args:
            error (ClientError): The exception raised by AWS SDK.
            secret_name (str): The name of the secret being retrieved.

        Raises:
            MissingSecretError: If the error code is 'ResourceNotFoundException'.
            MaxRetriesExceededError: For all other AWS ClientErrors after retries.
        """
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        metadata = self._build_metadata(secret_name, error, error_code=error_code)
        alert_message = f"Error retrieving secret '{secret_name}': {error_code}"

        handle_error(error, alert_message, logger, self.alerting, metadata)
        if error_code == "ResourceNotFoundException":
            raise MissingSecretError(secret_name)
        else:
            raise MaxRetriesExceededError(
                f"Failed to retrieve secret '{secret_name}' after {self.config.max_retries} attempts."
            ) from error

    def _build_metadata(
        self, secret_name: str, error: Exception, error_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build contextual metadata for alerting.

        Args:
            secret_name (str): The name of the secret involved.
            error (Exception): The exception that occurred.
            error_code (Optional[str]): The AWS error code, if available.

        Returns:
            Dict[str, Any]: A dictionary containing contextual metadata.
        """
        metadata = {
            "secret_name": secret_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "aws_region": self.aws_client_manager.region_name,
            "context": (
                "Async retrieval"
                if asyncio.iscoroutinefunction(self.get_secret_async)
                else "Sync retrieval"
            ),
        }
        if error_code:
            metadata["error_code"] = error_code
        return metadata
