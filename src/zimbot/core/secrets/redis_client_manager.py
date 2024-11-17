# src/core/secrets/redis_client_manager.py

import asyncio
import logging
from typing import Any, Callable, Optional, Type

import aioredis
import redis
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .alerting import Alerting  # Standardized alerting interface

# Import centralized decorators and configurations
from .circuit_breaker import with_circuit_breaker
from .config import get_redis_config  # Assuming a shared configuration module
from .error_handling import handle_error

logger = logging.getLogger(__name__)


class RedisClientManager:
    """
    Manages Redis clients for synchronous and asynchronous operations.
    Delegates cross-cutting concerns like circuit breaking and alerting to centralized modules.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        use_async: bool = False,
        circuit_breaker: Optional[
            Type
        ] = None,  # Replace with specific CircuitBreaker type if available
        alerting: Optional[Alerting] = None,
        max_async_connections: int = 10,
    ):
        """
        Initialize the RedisClientManager with minimal external logic.

        Args:
            redis_url (Optional[str]): Redis connection URL. Defaults to value from config.
            use_async (bool): Flag to determine if the manager should operate asynchronously.
            circuit_breaker (Optional[Type]): Circuit breaker instance for Redis operations.
            alerting (Optional[Alerting]): Alerting utility for sending alerts.
            max_async_connections (int): Maximum number of async connections in the pool.
        """
        config = get_redis_config()
        self.redis_url = redis_url or config.get(
            "REDIS_URL", "redis://localhost:6379/0"
        )
        self.use_async = use_async
        self.sync_client: Optional[redis.Redis] = None
        self.async_client: Optional[aioredis.Redis] = None
        self.circuit_breaker = circuit_breaker
        self.alerting = alerting
        self.max_async_connections = max_async_connections
        self._lock = asyncio.Lock()

    def _handle_error(self, error: Exception, message: str):
        """
        Centralized error handling; delegates alerting if configured.

        Args:
            error (Exception): The exception to handle.
            message (str): The error message.
        """
        handle_error(error, message, logger, self.alerting)

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((aioredis.RedisError, CachingError)),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    async def get_secret_async(self, key: str) -> Optional[str]:
        """
        Retrieve a secret asynchronously from Redis with retry and circuit breaker logic.

        Args:
            key (str): The Redis key to retrieve.

        Returns:
            Optional[str]: The retrieved secret, or None if not found.

        Raises:
            CachingError: If retrieving the secret fails after retries.
        """
        client = await self._get_async_client()
        try:
            value = await client.get(key)
            if value is not None:
                logger.debug("Async Redis cache hit.")
                return value
            else:
                logger.debug("Async Redis cache miss.")
                return None
        except Exception as e:
            self._handle_error(e, f"Failed to retrieve key '{key}' asynchronously")
            raise

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(redis.RedisError),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def get_secret_sync(self, key: str) -> Optional[str]:
        """
        Retrieve a secret synchronously from Redis with retry and circuit breaker logic.

        Args:
            key (str): The Redis key to retrieve.

        Returns:
            Optional[str]: The retrieved secret, or None if not found.

        Raises:
            CachingError: If retrieving the secret fails after retries.
        """
        client = self._get_sync_client()
        try:
            value = client.get(key)
            if value is not None:
                logger.debug("Sync Redis cache hit.")
                return value.decode("utf-8")
            else:
                logger.debug("Sync Redis cache miss.")
                return None
        except Exception as e:
            self._handle_error(e, f"Failed to retrieve key '{key}' synchronously")
            raise

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((aioredis.RedisError, CachingError)),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    async def set_secret_async(
        self, key: str, value: str, expire: Optional[int] = None
    ):
        """
        Set a secret asynchronously in Redis with retry and circuit breaker logic.

        Args:
            key (str): The Redis key to set.
            value (str): The value to set.
            expire (Optional[int]): Expiry time in seconds.

        Raises:
            CachingError: If setting the secret fails after retries.
        """
        client = await self._get_async_client()
        try:
            await client.set(key, value, ex=expire)
            logger.debug("Async Redis set successful.")
        except Exception as e:
            self._handle_error(e, f"Failed to set key '{key}' asynchronously")
            raise

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(redis.RedisError),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def set_secret_sync(self, key: str, value: str, expire: Optional[int] = None):
        """
        Set a secret synchronously in Redis with retry and circuit breaker logic.

        Args:
            key (str): The Redis key to set.
            value (str): The value to set.
            expire (Optional[int]): Expiry time in seconds.

        Raises:
            CachingError: If setting the secret fails after retries.
        """
        client = self._get_sync_client()
        try:
            client.set(key, value, ex=expire)
            logger.debug("Sync Redis set successful.")
        except Exception as e:
            self._handle_error(e, f"Failed to set key '{key}' synchronously")
            raise

    async def _get_async_client(self) -> aioredis.Redis:
        """
        Get or create an async Redis client.

        Returns:
            aioredis.Redis: The asynchronous Redis client pool.
        """
        async with self._lock:
            if self.async_client:
                try:
                    await self.async_client.ping()
                    logger.debug("Using existing asynchronous Redis client pool.")
                    return self.async_client
                except aioredis.RedisError:
                    logger.warning(
                        "Asynchronous Redis client pool is not alive. Recreating pool."
                    )
                    await self.close_async_client()

            try:
                self.async_client = aioredis.from_url(
                    self.redis_url,
                    max_connections=self.max_async_connections,
                    decode_responses=True,
                )
                await self.async_client.ping()
                logger.debug("Asynchronous Redis client pool created and is alive.")
            except aioredis.RedisError as e:
                self._handle_error(
                    e, "Failed to create or verify asynchronous Redis client pool"
                )
                raise CachingError(
                    "Failed to create or verify asynchronous Redis client pool"
                ) from e
            return self.async_client

    def _get_sync_client(self) -> redis.Redis:
        """
        Get or create a synchronous Redis client.

        Returns:
            redis.Redis: The synchronous Redis client.
        """
        if self.sync_client:
            try:
                if self.sync_client.ping():
                    logger.debug("Using existing synchronous Redis client.")
                    return self.sync_client
            except redis.RedisError:
                logger.warning(
                    "Synchronous Redis client is not alive. Recreating client."
                )

        try:
            self.sync_client = redis.Redis.from_url(self.redis_url)
            self.sync_client.ping()
            logger.debug("Synchronous Redis client created and is alive.")
        except redis.RedisError as e:
            self._handle_error(e, "Failed to create or verify synchronous Redis client")
            raise CachingError(
                "Failed to create or verify synchronous Redis client"
            ) from e
        return self.sync_client

    async def close_async_client(self):
        """
        Gracefully close the asynchronous Redis client pool.
        """
        if self.async_client:
            try:
                await self.async_client.close()
                logger.info("Asynchronous Redis client pool closed.")
            except Exception as e:
                self._handle_error(e, "Failed to close asynchronous Redis client pool")
            finally:
                self.async_client = None

    def close_sync_client(self):
        """
        Gracefully close the synchronous Redis client.
        """
        if self.sync_client:
            try:
                self.sync_client.close()
                logger.info("Synchronous Redis client closed.")
            except Exception as e:
                self._handle_error(e, "Failed to close synchronous Redis client")
            finally:
                self.sync_client = None

    async def simulate_failure(self):
        """
        Simulate Redis failure by closing both async and sync clients.
        Useful for testing circuit breakers and retry mechanisms.
        """
        logger.info("Simulating Redis failure.")
        await self.close_async_client()
        self.close_sync_client()

    async def recover_connection(self):
        """
        Recover Redis connection by re-initializing both async and sync clients.
        """
        logger.info("Attempting to recover Redis connection.")
        await self._get_async_client()
        self._get_sync_client()
        logger.info("Redis connection recovery successful.")

    async def close_all_clients(self):
        """
        Gracefully close both synchronous and asynchronous Redis clients.
        Should be called during application shutdown to prevent resource leaks.
        """
        await self.close_async_client()
        self.close_sync_client()
        logger.info("All Redis clients have been closed gracefully.")
