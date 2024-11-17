# src/zimbot/core/integrations/redis/redis_utils.py

import logging

import redis.asyncio as aioredis

from zimbot.core.config.settings import Settings, get_settings
from zimbot.core.integrations.exceptions.exceptions import (
    RedisConnectionError,
    RedisOperationError,
)

logger = logging.getLogger(__name__)

# Initialize settings
settings: Settings = get_settings()


class RedisClient:
    def __init__(self, redis_instance: aioredis.Redis) -> None:
        """
        Initialize the RedisClient with a Redis instance.

        Args:
            redis_instance (aioredis.Redis): The Redis client instance.
        """
        self.redis = redis_instance

    async def sadd(self, key: str, value: str) -> None:
        """
        Add a member to a set.

        Args:
            key (str): The key of the set.
            value (str): The value to add.

        Raises:
            RedisOperationError: If the operation fails.
        """
        try:
            await self.redis.sadd(key, value)
            logger.debug(f"Added value '{value}' to Redis set '{key}'.")
        except aioredis.RedisError as e:
            logger.error(f"Redis SADD operation failed: {e}")
            raise RedisOperationError("Failed to add value to Redis set") from e

    async def sismember(self, key: str, value: str) -> bool:
        """
        Check if a value is a member of a set.

        Args:
            key (str): The key of the set.
            value (str): The value to check.

        Returns:
            bool: True if the value is a member, False otherwise.

        Raises:
            RedisOperationError: If the operation fails.
        """
        try:
            result = await self.redis.sismember(key, value)
            logger.debug(
                f"Checked membership of '{value}' in Redis set '{key}': {result}"
            )
            return result
        except aioredis.RedisError as e:
            logger.error(f"Redis SISMEMBER operation failed: {e}")
            raise RedisOperationError("Failed to check membership in Redis set") from e

    async def flushall(self) -> None:
        """
        Flush all data from the Redis database.

        WARNING: This will delete all data in Redis.

        Raises:
            RedisOperationError: If the operation fails.
        """
        try:
            await self.redis.flushall()
            logger.info("Flushed all data from Redis.")
        except aioredis.RedisError as e:
            logger.error(f"Redis FLUSHALL operation failed: {e}")
            raise RedisOperationError("Failed to flush Redis data") from e

    async def close(self) -> None:
        """
        Close the Redis connection.

        Raises:
            RedisConnectionError: If closing fails.
        """
        try:
            await self.redis.close()
            await self.redis.wait_closed()
            logger.info("Closed Redis connection.")
        except aioredis.RedisError as e:
            logger.error(f"Failed to close Redis connection: {e}")
            raise RedisConnectionError("Failed to close Redis connection") from e
