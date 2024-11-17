from pydantic import AnyHttpUrl, Field, field_validator

from .base import BaseConfig


class APISettings(BaseConfig):
    """Settings for API server configuration."""

    base_url: AnyHttpUrl = Field(
        "http://localhost:8000",
        description="Base URL for the API, e.g., 'http://localhost:8000'.",
    )
    host: str = Field(
        "0.0.0.0", description="Host address for the API server, e.g., '0.0.0.0'."
    )
    port: int = Field(
        8000, ge=1, le=65535, description="Port number for the API server."
    )

    model_config = {
        "env_prefix": "API_",  # Set environment variable prefix for the fields
    }

    @field_validator("base_url")
    def validate_base_url(cls, v: AnyHttpUrl) -> AnyHttpUrl:
        # Convert `v` to a string before validation
        url_str = str(v)
        if not (url_str.startswith("http://") or url_str.startswith("https://")):
            raise ValueError("base_url must start with 'http://' or 'https://'")
        return v
