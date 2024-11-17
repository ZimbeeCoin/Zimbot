# src/core/secrets/secrets_manager.py

"""
High-level SecretsManager orchestrating secrets retrieval, caching, alerting, encryption, and key rotation.
Implements Singleton pattern and supports asynchronous context management.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional

import sentry_sdk  # Ensure sentry_sdk is imported for error tracking

from .alerting import Alerting
from .aws_client_manager import AWSSecretsClientManager
from .caching import Caching
from .circuit_breaker import CircuitBreakerManager, with_circuit_breaker
from .config_validation import (
    AlertingConfig,
    SecretsManagerConfig,
    SMTPConfig,
    validate_env_variables,
)
from .encryption import EncryptionManager
from .exceptions import (
    ConfigurationValidationError,
    MaxRetriesExceededError,
    MissingSecretError,
)
from .health_check import SecretsManagerHealthCheck
from .metrics import cache_hit_counter, cache_miss_counter, secrets_retrieval_latency
from .metrics_server import start_metrics_server
from .redis_client_manager import RedisClientManager
from .rotation import SecretsRotator
from .secrets_logger import get_logger
from .secrets_retriever import SecretsRetriever

logger = get_logger(__name__)


class SecretsManager:
    """
    High-level SecretsManager that orchestrates secrets retrieval, caching, alerting, encryption, and rotation.
    Implements Singleton pattern and supports asynchronous context management.
    """

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Implement Singleton pattern to ensure only one instance exists.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        use_async: bool = False,
        aws_region: Optional[str] = None,
        redis_url: Optional[str] = None,
        alerting: Optional[Alerting] = None,
        encryption_key: Optional[str] = None,  # Current encryption key
        previous_encryption_keys: Optional[
            List[str]
        ] = None,  # Previous encryption keys
        use_secrets_manager: bool = False,
        secret_names: Optional[List[str]] = None,  # For rotation
        rotation_interval: int = 86400,  # 24 hours
        metrics_port: int = 8000,
        circuit_breaker_manager: Optional[CircuitBreakerManager] = None,
    ):
        """
        Initialize the SecretsManager.

        Args:
            use_async (bool): Flag to determine if the manager should operate asynchronously.
            aws_region (Optional[str]): AWS region name. Defaults to 'AWS_REGION' env var.
            redis_url (Optional[str]): Redis connection URL. Defaults to 'REDIS_URL' env var.
            alerting (Optional[Alerting]): Alerting utility for sending alerts. If not provided, initializes with environment config.
            encryption_key (Optional[str]): Encryption key for encrypting secrets before caching.
            previous_encryption_keys (Optional[List[str]]): List of previous encryption keys for decryption.
            use_secrets_manager (bool): Flag to determine if AWS Secrets Manager should be used.
            secret_names (Optional[List[str]]): List of secret names to rotate. If None, no rotation.
            rotation_interval (int): Interval in seconds between rotations.
            metrics_port (int): Port number for Prometheus metrics server.
            circuit_breaker_manager (Optional[CircuitBreakerManager]): Instance managing circuit breakers.
        """
        # Prevent re-initialization
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.use_async = use_async
        self.use_secrets_manager = use_secrets_manager
        self.logger = logger

        # Validate environment variables
        validate_env_variables()
        self.config = SecretsManagerConfig(
            use_async=self.use_async,
            aws_region=aws_region or os.getenv("AWS_REGION"),
            redis_url=redis_url or os.getenv("REDIS_URL"),
            cache_ttl=int(os.getenv("CACHE_TTL", 300)),
            redis_expiry_seconds=int(os.getenv("REDIS_EXPIRY_SECONDS", 600)),
            encryption_key=encryption_key,
            use_secrets_manager=use_secrets_manager,
            secret_names=secret_names,
            rotation_interval=rotation_interval,
            alerting=AlertingConfig(
                email_alerts=[
                    email.strip()
                    for email in os.getenv("ALERT_EMAILS", "").split(",")
                    if email.strip()
                ],
                slack_webhooks=[
                    webhook.strip()
                    for webhook in os.getenv("SLACK_WEBHOOKS", "").split(",")
                    if webhook.strip()
                ],
                webhook_urls=[
                    webhook.strip()
                    for webhook in os.getenv("GENERIC_WEBHOOKS", "").split(",")
                    if webhook.strip()
                ],
                smtp_config=SMTPConfig(
                    hostname=os.getenv("SMTP_HOST"),
                    port=int(os.getenv("SMTP_PORT", 587)),
                    username=os.getenv("SMTP_USERNAME"),
                    password=os.getenv("SMTP_PASSWORD"),
                    from_email=os.getenv("SMTP_FROM_EMAIL"),
                    start_tls=os.getenv("SMTP_START_TLS", "True").lower()
                    in ["true", "1", "yes"],
                ),
            ),
        )
        self.logger.debug("Environment variables validated successfully.")

        # Initialize Alerting
        self.alerting = alerting or Alerting(
            email_alerts=self.config.alerting.email_alerts,
            slack_webhooks=self.config.alerting.slack_webhooks,
            webhook_urls=self.config.alerting.webhook_urls,
            smtp_config=self.config.alerting.smtp_config.dict(),
        )

        # Initialize CircuitBreakerManager
        self.circuit_breaker_manager = circuit_breaker_manager or CircuitBreakerManager(
            alerting=self.alerting
        )

        # Initialize AWS Secrets Manager Client Manager with Circuit Breaker
        self.aws_client_manager = AWSSecretsClientManager(
            use_async=self.use_async,
            region_name=self.config.aws_region,
            circuit_breaker=self.circuit_breaker_manager.get_aws_circuit_breaker(),
            alerting=self.alerting,
        )

        # Initialize Redis Client Manager with Circuit Breaker
        self.redis_client_manager = RedisClientManager(
            redis_url=self.config.redis_url,
            use_async=self.use_async,
            circuit_breaker=self.circuit_breaker_manager.get_redis_circuit_breaker(),
            alerting=self.alerting,
        )

        # Initialize Caching
        self.caching = Caching(
            redis_enabled=bool(self.config.redis_url),
            redis_available=False,  # Will be set after connection
            cache_ttl=self.config.cache_ttl,
            redis_expiry_seconds=self.config.redis_expiry_seconds,
            cipher=None,  # To be set if encryption is implemented
            cache_hit_counter=cache_hit_counter,
            cache_miss_counter=cache_miss_counter,
        )

        # Initialize EncryptionManager with Circuit Breaker
        if self.config.encryption_key:
            keys = [self.config.encryption_key] + (previous_encryption_keys or [])
            self.encryption_manager = EncryptionManager(
                config=self.config,
                storage_client=KeyStorageClient(),
                circuit_breaker=self.circuit_breaker_manager.get_encryption_circuit_breaker(),
            )
            self.encryption_manager.load_keys_from_secure_storage()
            self.caching.cipher = self.encryption_manager
            logger.debug("EncryptionManager initialized with key rotation support.")
        else:
            self.encryption_manager = None

        # Initialize SecretsRetriever with Circuit Breaker
        self.secrets_retriever = SecretsRetriever(
            aws_client_manager=self.aws_client_manager,
            caching=self.caching,
            alerting=self.alerting,
            metrics=None,  # To be implemented if metrics are needed
        )

        # Initialize HealthCheck
        self.health_check = SecretsManagerHealthCheck(
            aws_client_manager=self.aws_client_manager,
            redis_client_manager=self.redis_client_manager,
            encryption_manager=self.encryption_manager,
        )

        # Initialize SecretsRotator if secret_names are provided
        if self.config.secret_names and self.encryption_manager:
            self.secrets_rotator = SecretsRotator(
                secrets_retriever=self.secrets_retriever,
                encryption_manager=self.encryption_manager,
                secret_names=self.config.secret_names,
                interval=self.config.rotation_interval,
                alerting=self.alerting,
            )
            if self.use_async:
                self.secrets_rotator.start_rotation()
        else:
            self.secrets_rotator = None

        # Start Metrics Server
        start_metrics_server(self.config.metrics_port)
        logger.debug(f"Metrics server started on port {self.config.metrics_port}.")

        self._initialized = True
        self.logger.debug("SecretsManager initialized successfully.")

    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance. Useful for testing or resetting state.
        """
        cls._instance = None
        logger.debug("SecretsManager singleton instance has been reset.")

    @staticmethod
    def create(use_async: bool = False) -> "SecretsManager":
        """
        Factory method to create a SecretsManager instance based on SECRETS_PROVIDER.

        Args:
            use_async (bool): Flag to determine if the manager should operate asynchronously.

        Returns:
            SecretsManager: Configured SecretsManager instance.

        Raises:
            ConfigurationValidationError: If SECRETS_PROVIDER is invalid.
        """
        provider = os.getenv("SECRETS_PROVIDER", "env").lower()
        if provider == "aws":
            return SecretsManager(use_async=use_async, use_secrets_manager=True)
        elif provider == "env":
            return SecretsManager(use_async=use_async, use_secrets_manager=False)
        else:
            raise ConfigurationValidationError(
                "Invalid SECRETS_PROVIDER value. Choose 'aws' or 'env'."
            )

    async def __aenter__(self):
        """
        Async context manager entry. Initialize Redis connection if using async.
        """
        if self.use_async:
            # Initialize Redis connection
            if self.caching.redis_enabled:
                try:
                    await self.redis_client_manager.create_async_redis_pool()
                    self.caching.redis_available = True
                    self.logger.info("Connected to Redis successfully (Async).")
                except Exception as e:
                    self.caching.redis_available = False
                    self.logger.error(f"Failed to connect to Redis (Async): {e}")
                    sentry_sdk.capture_exception(e)
                    await self.alerting.send_alert(
                        f"Failed to connect to Redis (Async): {e}"
                    )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Async context manager exit. Clean up Redis connections and rotation task.
        """
        if self.use_async:
            # Close Redis connection
            if self.redis_client_manager.async_client:
                await self.redis_client_manager.close_async_client()
                self.caching.redis_available = False
                self.logger.info("Redis connection closed (Async).")

            # Stop rotation task
            if self.secrets_rotator:
                self.secrets_rotator.stop_rotation()

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_aws_circuit_breaker()
    )
    async def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret asynchronously.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The retrieved secret.

        Raises:
            MissingSecretError: If the secret is missing.
            Exception: For other retrieval issues.
        """
        return await self.secrets_retriever.get_secret_async(secret_name)

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_redis_circuit_breaker()
    )
    def get_secret_sync(self, secret_name: str) -> str:
        """
        Retrieve a secret synchronously.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The retrieved secret.

        Raises:
            MissingSecretError: If the secret is missing.
            Exception: For other retrieval issues.
        """
        return self.secrets_retriever.get_secret_sync(secret_name)

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_redis_circuit_breaker()
    )
    async def refresh_secret(self, secret_name: str) -> str:
        """
        Refresh a specific secret asynchronously.

        Args:
            secret_name (str): The name of the secret to refresh.

        Returns:
            str: The refreshed secret value.

        Raises:
            Exception: If refreshing fails.
        """
        return await self.secrets_retriever.refresh_secret_async(secret_name)

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_redis_circuit_breaker()
    )
    def refresh_secret_sync(self, secret_name: str) -> str:
        """
        Refresh a specific secret synchronously.

        Args:
            secret_name (str): The name of the secret to refresh.

        Returns:
            str: The refreshed secret value.

        Raises:
            Exception: If refreshing fails.
        """
        return self.secrets_retriever.refresh_secret_sync(secret_name)

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_aws_circuit_breaker()
    )
    async def refresh_all_secrets(
        self, secret_names: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Refresh multiple secrets asynchronously.

        Args:
            secret_names (List[str]): List of secret names to refresh.

        Returns:
            Dict[str, Optional[str]]: Dictionary mapping secret names to their refreshed values.

        Raises:
            Exception: If any secret fails to refresh.
        """
        return await self.secrets_retriever.refresh_all_secrets_async(secret_names)

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_aws_circuit_breaker()
    )
    def refresh_all_secrets_sync(
        self, secret_names: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Refresh multiple secrets synchronously.

        Args:
            secret_names (List[str]): List of secret names to refresh.

        Returns:
            Dict[str, Optional[str]]: Dictionary mapping secret names to their refreshed values.

        Raises:
            Exception: If any secret fails to refresh.
        """
        return self.secrets_retriever.refresh_all_secrets_sync(secret_names)

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_encryption_circuit_breaker()
    )
    async def rotate_encryption_key(self, new_key: str):
        """
        Rotate the encryption key by adding a new key to the EncryptionManager.

        Args:
            new_key (str): The new base64-encoded encryption key.

        Raises:
            RuntimeError: If EncryptionManager is not initialized.
        """
        if not self.encryption_manager:
            raise RuntimeError("EncryptionManager is not initialized.")
        try:
            self.encryption_manager.rotate_keys([new_key])
            self.logger.info("Encryption key rotated successfully.")
            await self.alerting.send_alert("Encryption key rotated successfully.")
        except Exception as e:
            self.logger.error(f"Encryption key rotation failed: {e}")
            await self.alerting.send_alert(f"Encryption key rotation failed: {e}")
            raise

    def close_sync_clients(self):
        """
        Closes synchronous clients (AWSSecretsClientManager and RedisClientManager).
        """
        if not self.use_async:
            try:
                self.aws_client_manager.get_sync_client().close()
                self.redis_client_manager.close_sync_client()
                self.logger.info("Synchronous clients closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing synchronous clients: {e}")
                if self.alerting and self.circuit_breaker_manager:
                    asyncio.run(
                        self.alerting.send_alert(
                            f"Error closing synchronous clients: {e}"
                        )
                    )
                handle_error(e, "SecretsManager", logger, self.alerting)
                raise
