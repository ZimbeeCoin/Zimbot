# src/zimbot/core/config/rate_limit_config.py

from typing import Literal

from pydantic import Field, validator

from .base import BaseConfig


class RateLimitSettings(BaseConfig):
    """Rate limiting configuration."""

    enable_rate_limit: bool = Field(
        default=True,
        description="Enable or disable rate limiting.",
    )
    rate_limit_storage: Literal["memory", "redis"] = Field(
        default="memory",
        description="Storage backend for rate limiting, e.g., 'memory' or 'redis'.",
    )
    default_rate_limit: str = Field(
        default="100/minute",
        description="Default rate limit for endpoints, e.g., '100/minute'.",
    )
    market_rate_limit: str = Field(
        default="100/minute",
        description="Rate limit for market-related endpoints.",
    )
    consult_rate_limit: str = Field(
        default="50/minute",
        description="Rate limit for consultation-related endpoints.",
    )
    assistant_rate_limit: str = Field(
        default="30/minute",
        description="Rate limit for assistant-related endpoints.",
    )
    bot_rate_limit: str = Field(
        default="60/minute",
        description="Rate limit for bot-related endpoints.",
    )
    auth_rate_limit: str = Field(
        default="20/minute",
        description="Rate limit for authentication-related endpoints.",
    )
    subscriptions_rate_limit: str = Field(
        default="40/minute",
        description="Rate limit for subscription-related endpoints.",
    )

    model_config = {
        "env_prefix": "RATE_LIMIT_",
    }

    @validator("rate_limit_storage")
    def validate_storage(cls, v: str) -> str:
        """
        Validate that the rate limit storage backend is valid.
        """
        valid_storage = {"memory", "redis"}
        if v not in valid_storage:
            raise ValueError(f"rate_limit_storage must be one of {valid_storage}")
        return v.lower()
