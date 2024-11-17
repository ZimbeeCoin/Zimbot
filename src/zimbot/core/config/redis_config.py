from typing import Optional

from pydantic import AnyUrl, Field

from .base import BaseConfig


class RedisSettings(BaseConfig):
    """Settings for Redis connection."""

    enabled: bool = Field(
        default=False,
        description="Enable or disable Redis caching."
    )
    url: AnyUrl = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL, e.g., 'redis://localhost:6379/0'."
    )
    host: str = Field(
        default="localhost",
        description="Redis host address, e.g., 'localhost' or 'redis-server.com'."
    )
    port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis server port, e.g., 6379."
    )
    db: int = Field(
        default=0,
        ge=0,
        description="Redis database number, default is 0."
    )
    password: Optional[str] = Field(
        default=None,
        description="Password for Redis server. None if no password is required."
    )
    minsize: int = Field(
        default=1,
        ge=1,
        description="Minimum number of connections in the Redis pool."
    )
    maxsize: int = Field(
        default=10,
        ge=1,
        description="Maximum number of connections in the Redis pool."
    )
    expire_seconds: int = Field(
        default=3600,
        ge=60,
        description="Expiration time for cached secrets in Redis."
    )
    cache_ttl: int = Field(
        default=300,
        ge=1,
        description="Time-to-live for cache entries, in seconds."
    )

    # Model configuration for Pydantic v2 compatibility
    model_config = {
        "env_prefix": "REDIS_",
    }
