from typing import Optional

from pydantic import Field, SecretStr, field_validator

from .base import BaseConfig


class NgrokSettings(BaseConfig):
    """Settings for Ngrok integration."""

    api_name: Optional[str] = Field(
        default=None, description="API name for Ngrok."
    )
    api_key: SecretStr = Field(
        ..., description="API key for Ngrok."
    )
    auth_token: SecretStr = Field(
        ..., description="Authentication token for Ngrok."
    )

    model_config = {
        "env_prefix": "NGROK_",
    }

    @field_validator("auth_token")
    def validate_auth_token(cls, v: SecretStr) -> SecretStr:
        """
        Validate the authentication token.
        """
        token = v.get_secret_value()
        if len(token) < 10:
            raise ValueError(
                "NGROK_AUTH_TOKEN must be at least 10 characters long."
            )
        return v

    @field_validator("api_key")
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """
        Validate the API key.
        """
        key = v.get_secret_value()
        if len(key) < 10:
            raise ValueError(
                "NGROK_API_KEY must be at least 10 characters long."
            )
        return v

    @field_validator("api_name")
    def validate_api_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate the API name, if provided.
        """
        if v and not v.isidentifier():
            raise ValueError(
                "API name must be a valid identifier (letters, digits, or underscores)."
            )
        return v
