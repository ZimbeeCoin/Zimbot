# src/core/config/streaming_config.py

from typing import Optional

from pydantic import Field, model_validator

from .base import BaseConfig


class StreamingConfig(BaseConfig):
    """Advanced streaming configuration for OpenAI and related integrations."""

    timeout: int = Field(
        default=120,
        ge=1,
        description="Timeout in seconds for streaming responses from OpenAI API.",
    )
    max_chunk_size: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum size for streamed chunks in bytes. "
                    "Set to None to allow unlimited chunk size.",
    )
    buffer_size: int = Field(
        default=4096,
        ge=512,
        description="Buffer size in bytes for managing streamed data.",
    )
    retries: int = Field(
        default=3,
        ge=0,
        description="Number of retries for failed streaming requests.",
    )
    backoff_factor: float = Field(
        default=0.5,
        ge=0.1,
        description=(
            "Backoff factor for retries. Defines the delay between retry attempts."
        ),
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable or disable debug mode for streaming.",
    )

    model_config = {
        "env_prefix": "STREAMING_",
    }

    @model_validator(mode="after")
    def validate_streaming_settings(self):
        """
        Perform additional validations on streaming settings.
        """
        if self.max_chunk_size and self.max_chunk_size < self.buffer_size:
            raise ValueError(
                "max_chunk_size must be greater than or equal to buffer_size "
                "to prevent data loss."
            )
        if self.timeout < self.retries * self.backoff_factor:
            raise ValueError(
                "Timeout must be greater than the total retry delay "
                "(retries * backoff_factor)."
            )
        return self
