from pydantic import AnyHttpUrl, Field, field_validator

from .base import BaseConfig


class CoinAPISettings(BaseConfig):
    """Settings for CoinAPI integration."""

    base_url: AnyHttpUrl = Field(
        "https://rest.coinapi.io/", description="Base URL for CoinAPI."
    )
    api_key: str = Field(
        ..., description="API key for accessing CoinAPI."
    )  # Environment variable handling moved to model_config
    timeout: int = Field(
        30, ge=1, description="Request timeout in seconds for CoinAPI."
    )
    retry_attempts: int = Field(
        3, ge=0, description="Number of retry attempts for failed requests."
    )

    # Corrected model_config usage
    model_config = {
        "env_prefix": "COINAPI_",  # Prefix for environment variables
    }

    @field_validator("base_url")
    def validate_base_url(cls, v: AnyHttpUrl) -> AnyHttpUrl:
        url_str = str(v)  # Convert AnyHttpUrl to string for validation
        if not (url_str.startswith("http://") or url_str.startswith("https://")):
            raise ValueError("base_url must start with 'http://' or 'https://'")
        return v
