# src/core/secrets/caching.py

"""
Module for managing caching of secrets, supporting in-memory and Redis-based caching.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from ..alerting import Alerting
from ..config import get_cache_config  # Assuming a shared configuration module
from ..error_handling import handle_error
from ..exceptions import CachingError
from .metrics import cache_hit_counter, cache_miss_counter
from .redis_client_manager import RedisClientManager
from .secondary_cache import SecondaryCache

logger = logging.getLogger(__name__)


class Caching:
    """
    Manages caching for secrets, supporting both in-memory and Redis-based caches.
    Delegates cross-cutting concerns like error handling and alerting to centralized modules.
    """

    def __init__(
        self,
        redis_manager: RedisClientManager,
        secondary_cache: Optional[SecondaryCache] = None,
        cache_ttl: int = 300,
        redis_expiry_seconds: int = 600,
        cipher: Optional[Any] = None,  # Placeholder for EncryptionManager's cipher
        alerting: Optional[Alerting] = None,
    ):
        """
        Initialize the Caching manager.

        Args:
            redis_manager (RedisClientManager): Injected RedisClientManager for distributed caching.
            secondary_cache (Optional[SecondaryCache]): Injected secondary cache for fallback.
            cache_ttl (int): Time-to-live for in-memory cache entries in seconds.
            redis_expiry_seconds (int): Expiry time for Redis cache entries in seconds.
            cipher (Optional[Any]): Cipher for encrypting secrets before caching.
            alerting (Optional[Alerting]): Alerting utility for sending alerts.
        """
        config = get_cache_config()
        self.redis_manager = redis_manager
        self.secondary_cache = secondary_cache or SecondaryCache()
        self.cache_ttl = cache_ttl or config.get("CACHE_TTL", 300)
        self.redis_expiry_seconds = redis_expiry_seconds or config.get(
            "REDIS_EXPIRY_SECONDS", 600
        )
        self.cipher = cipher
        self.alerting = alerting

        # In-memory cache: {secret_name: {"value": secret_value, "expiry": timestamp}}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def _handle_error(self, error: Exception, message: str):
        """
        Centralized error handling; delegates alerting if configured.

        Args:
            error (Exception): The exception to handle.
            message (str): The error message.
        """
        handle_error(error, message, logger, self.alerting)

    async def get_cached_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret from the cache.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            Optional[str]: The cached secret value, or None if not found or expired.

        Raises:
            CachingError: If retrieval fails due to unexpected errors.
        """
        current_time = asyncio.get_event_loop().time()

        # Check in-memory cache
        async with self._lock:
            entry = self._cache.get(secret_name)
            if entry and entry["expiry"] > current_time:
                cache_hit_counter.inc()
                logger.debug(f"Cache hit (in-memory) for secret '{secret_name}'.")
                return entry["value"]
            elif entry:
                # Expired
                del self._cache[secret_name]
                logger.debug(f"Cache entry expired for secret '{secret_name}'.")

        # Check Redis cache via RedisClientManager
        if self.redis_manager.redis_enabled and self.redis_manager.is_available:
            try:
                cached = await self.redis_manager.get_secret_async(secret_name)
                if cached:
                    secret_value = self._decrypt(cached)
                    cache_hit_counter.inc()
                    logger.debug(f"Cache hit (Redis) for secret '{secret_name}'.")
                    # Refresh in-memory cache
                    async with self._lock:
                        self._cache[secret_name] = {
                            "value": secret_value,
                            "expiry": current_time + self.cache_ttl,
                        }
                    # Also set in secondary cache
                    await self.secondary_cache.set(secret_name, secret_value)
                    return secret_value
            except CachingError as e:
                self._handle_error(e, f"Error retrieving '{secret_name}' from Redis")
                # Optionally, mark Redis as unavailable or take other actions

        # Check Secondary Cache
        try:
            secret = await self.secondary_cache.get(secret_name)
            if secret:
                cache_hit_counter.inc()
                logger.debug(f"Cache hit (secondary cache) for secret '{secret_name}'.")
                return secret
        except Exception as e:
            self._handle_error(
                e, f"Error retrieving '{secret_name}' from Secondary Cache"
            )

        # Cache miss
        cache_miss_counter.inc()
        logger.debug(f"Cache miss for secret '{secret_name}'.")
        return None

    async def set_cached_secret(self, secret_name: str, secret_value: str):
        """
        Cache a secret in both in-memory and Redis caches.

        Args:
            secret_name (str): The name of the secret.
            secret_value (str): The value of the secret.

        Raises:
            CachingError: If caching fails due to unexpected errors.
        """
        current_time = asyncio.get_event_loop().time()
        encrypted_value = self._encrypt(secret_value)

        # Set in-memory cache
        async with self._lock:
            self._cache[secret_name] = {
                "value": secret_value,
                "expiry": current_time + self.cache_ttl,
            }
        logger.debug(
            f"Secret '{secret_name}' cached in-memory with TTL {self.cache_ttl}s."
        )

        # Set Redis cache via RedisClientManager
        if self.redis_manager.redis_enabled and self.redis_manager.is_available:
            try:
                await self.redis_manager.set_secret_async(
                    secret_name, encrypted_value, expire=self.redis_expiry_seconds
                )
                logger.debug(
                    f"Secret '{secret_name}' cached in Redis with expiry {self.redis_expiry_seconds}s."
                )
            except CachingError as e:
                self._handle_error(e, f"Error setting '{secret_name}' in Redis")
                # Optionally, mark Redis as unavailable or take other actions

        # Set Secondary Cache
        try:
            await self.secondary_cache.set(secret_name, secret_value)
        except Exception as e:
            self._handle_error(e, f"Error setting '{secret_name}' in Secondary Cache")

    async def remove_cached_secret(self, secret_name: str):
        """
        Remove a secret from both in-memory and Redis caches.

        Args:
            secret_name (str): The name of the secret to remove.

        Raises:
            CachingError: If removal fails due to unexpected errors.
        """
        # Remove from in-memory cache
        async with self._lock:
            removed = self._cache.pop(secret_name, None)
        if removed:
            logger.debug(f"Secret '{secret_name}' removed from in-memory cache.")

        # Remove from Redis cache via RedisClientManager
        if self.redis_manager.redis_enabled and self.redis_manager.is_available:
            try:
                await self.redis_manager.remove_secret_async(secret_name)
                logger.debug(f"Secret '{secret_name}' removed from Redis cache.")
            except CachingError as e:
                self._handle_error(e, f"Error removing '{secret_name}' from Redis")
                # Optionally, mark Redis as unavailable or take other actions

        # Remove from Secondary Cache
        try:
            await self.secondary_cache.remove(secret_name)
            logger.debug(f"Secret '{secret_name}' removed from Secondary Cache.")
        except Exception as e:
            self._handle_error(
                e, f"Error removing '{secret_name}' from Secondary Cache"
            )

    def _encrypt(self, plaintext: str) -> str:
        """
        Encrypt the plaintext using the provided cipher.

        Args:
            plaintext (str): The plaintext to encrypt.

        Returns:
            str: The encrypted text.
        """
        if self.cipher:
            try:
                return self.cipher.encrypt(plaintext)
            except Exception as e:
                self._handle_error(e, "Encryption failed")
                raise CachingError("Encryption failed") from e
        return plaintext  # No encryption if cipher not provided

    def _decrypt(self, ciphertext: str) -> str:
        """
        Decrypt the ciphertext using the provided cipher.

        Args:
            ciphertext (str): The ciphertext to decrypt.

        Returns:
            str: The decrypted text.
        """
        if self.cipher:
            try:
                return self.cipher.decrypt(ciphertext)
            except Exception as e:
                self._handle_error(e, "Decryption failed")
                raise CachingError("Decryption failed") from e
        return ciphertext  # No decryption if cipher not provided

    async def close(self):
        """
        Gracefully close any resources if needed.
        """
        # Currently, RedisClientManager handles its own closing.
        # If SecondaryCache or other resources need closing, handle them here.
        await self.secondary_cache.close()
        logger.info("Caching manager resources have been closed.")
