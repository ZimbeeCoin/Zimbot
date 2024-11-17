# src/core/secrets/secondary_cache.py

"""
Module for managing a secondary in-memory cache for failover scenarios.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SecondaryCache:
    """
    Manages a secondary in-memory cache for secrets as a failover mechanism.
    """

    def __init__(self):
        """
        Initialize the SecondaryCache.
        """
        self._cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get(self, secret_name: str) -> Optional[Any]:
        """
        Retrieve a secret from the secondary cache.

        Args:
            secret_name (str): The name of the secret.

        Returns:
            Optional[Any]: The secret value or None if not found.
        """
        async with self._lock:
            secret = self._cache.get(secret_name)
            if secret:
                logger.debug(f"Secondary cache hit for secret '{secret_name}'.")
            else:
                logger.debug(f"Secondary cache miss for secret '{secret_name}'.")
            return secret

    async def set(self, secret_name: str, secret_value: Any):
        """
        Set a secret in the secondary cache.

        Args:
            secret_name (str): The name of the secret.
            secret_value (Any): The value of the secret.
        """
        async with self._lock:
            self._cache[secret_name] = secret_value
            logger.debug(f"Secret '{secret_name}' set in secondary cache.")

    async def remove(self, secret_name: str):
        """
        Remove a secret from the secondary cache.

        Args:
            secret_name (str): The name of the secret to remove.
        """
        async with self._lock:
            if secret_name in self._cache:
                del self._cache[secret_name]
                logger.debug(f"Secret '{secret_name}' removed from secondary cache.")

    async def clear(self):
        """
        Clear all secrets from the secondary cache.
        """
        async with self._lock:
            self._cache.clear()
            logger.info("Secondary cache cleared.")
