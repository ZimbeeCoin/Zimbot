# src/core/integrations/redis/redis_client.py

from typing import AsyncGenerator

import aioredis

from zimbot.core.config.config import settings


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(
        settings.redis.url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,  # Adjust based on your load
    )
    try:
        yield redis
    finally:
        await redis.close()
