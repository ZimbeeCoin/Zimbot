import json
from typing import List

from pydantic import AnyHttpUrl, Field, validator

from .base import BaseConfig


class CORSSettings(BaseConfig):
    """Settings for Cross-Origin Resource Sharing (CORS)."""

    allowed_origins: List[AnyHttpUrl] = Field(
        [],
        description="List of allowed origins for CORS.",
    )
    allowed_methods: List[str] = Field(
        ["GET", "POST", "OPTIONS"],
        description="HTTP methods allowed for CORS.",
    )
    allowed_headers: List[str] = Field(
        ["Authorization", "Content-Type", "Accept"],
        description="HTTP headers allowed for CORS.",
    )
    allow_credentials: bool = Field(
        True, description="Whether to allow credentials in CORS."
    )
    max_age: int = Field(
        3600, description="Time in seconds for caching preflight responses."
    )
    expose_headers: List[str] = Field(
        ["Content-Length", "X-Kuma-Revision"],
        description="HTTP headers to expose to the browser.",
    )

    # Replace inner Config class with model_config
    model_config = BaseConfig.model_config.copy(
        env_prefix="CORS_"  # type: ignore
    )

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """
        Parse the allowed_origins from a JSON string or list.
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "allowed_origins must be a valid JSON list of URLs."
                ) from e
        return v
