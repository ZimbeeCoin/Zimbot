from typing import Literal

from pydantic import Field, SecretStr, field_validator

from .base import BaseConfig


class JWTSettings(BaseConfig):
    """Settings for JSON Web Token (JWT) configuration."""

    secret_key: SecretStr = Field(
        ..., description="Secret key used for signing JWT tokens."
    )
    algorithm: Literal[
        "HS256", "HS384", "HS512", "RS256", "RS384", "RS512"
    ] = Field(
        "HS256", description="Algorithm used for JWT encoding and decoding."
    )
    access_token_expire_minutes: int = Field(
        60, ge=1, description="Expiration time in minutes for access tokens."
    )
    refresh_token_expire_days: int = Field(
        7, ge=1, description="Expiration time in days for refresh tokens."
    )

    model_config = {
        "env_prefix": "JWT_",
    }

    @field_validator("secret_key")
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long.")
        return v

    @field_validator("algorithm")
    def validate_algorithm(cls, v: str) -> str:
        allowed_algorithms = {
            "HS256", "HS384", "HS512", "RS256", "RS384", "RS512"
        }
        if v not in allowed_algorithms:
            raise ValueError(
                f"Invalid JWT algorithm: {v}. Allowed: {', '.join(allowed_algorithms)}"
            )
        return v
