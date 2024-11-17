from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator

from .base import BaseConfig


class OpenAISettings(BaseConfig):
    """Settings for OpenAI API integration."""

    default_model: str = Field(
        default="gpt-4o",
        description="Default model for OpenAI API requests.",
    )
    backup_model: str = Field(
        default="gpt-4o-mini",
        description="Backup model to use if the default fails.",
    )
    api_version: Literal["v1"] = Field(
        default="v1",
        description="API version for OpenAI.",
    )
    base_url: AnyHttpUrl = Field(
        default="https://api.openai.com/v1/",
        description="Base URL for OpenAI API.",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries for API requests.",
    )
    request_timeout: int = Field(
        default=60,
        ge=1,
        description="Timeout in seconds for API requests.",
    )
    connect_timeout: int = Field(
        default=10,
        ge=1,
        description="Connection timeout in seconds.",
    )
    read_timeout: int = Field(
        default=30,
        ge=1,
        description="Read timeout in seconds.",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for detailed logging.",
    )

    model_config = {
        "env_prefix": "OPENAI_",
    }

    @field_validator("base_url")
    def validate_base_url(cls, v: AnyHttpUrl) -> AnyHttpUrl:
        """Ensure base_url starts with http:// or https://."""
        url_str = str(v)
        if not (url_str.startswith("http://") or url_str.startswith("https://")):
            raise ValueError("base_url must start with 'http://' or 'https://'.")
        return v

    @field_validator("default_model", "backup_model")
    def validate_model_name(cls, v: str) -> str:
        """Validate model names to ensure compatibility with OpenAI."""
        allowed_models = {
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5",
            "gpt-3.5-turbo",
        }
        if v not in allowed_models:
            raise ValueError(
                f"Model '{v}' is not supported. Allowed models: "
                f"{', '.join(allowed_models)}"
            )
        return v
