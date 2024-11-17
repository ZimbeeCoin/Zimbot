from typing import Optional

from pydantic import Field, SecretStr, model_validator

from .base import BaseConfig


class StripeSettings(BaseConfig):
    """Settings for Stripe API integration."""

    api_key: SecretStr = Field(
        ...,
        description="Publishable API key for Stripe.",
    )
    api_secret_key: SecretStr = Field(
        ...,
        description="Secret API key for Stripe.",
    )
    webhook_secret: Optional[SecretStr] = Field(
        None,
        description="Webhook secret for Stripe. Required only in production.",
    )
    currency: str = Field(
        default="USD",
        description="Default currency for Stripe transactions.",
    )
    retry_attempts: int = Field(
        default=3,
        ge=0,
        description="Number of retry attempts for failed Stripe API requests.",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        description="Timeout in seconds for Stripe API requests.",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for verbose logging of Stripe API interactions.",
    )

    # Replace `Config` with `model_config` for Pydantic v2 compatibility
    model_config = {
        "env_prefix": "STRIPE_",
    }

    @model_validator(mode="after")
    def validate_keys(self):
        """
        Validate that API keys are set and meet minimum requirements.
        """
        if len(self.api_key.get_secret_value()) < 10:
            raise ValueError("API key must be at least 10 characters long.")
        if len(self.api_secret_key.get_secret_value()) < 10:
            raise ValueError("API secret key must be at least 10 characters long.")
        if self.webhook_secret and len(self.webhook_secret.get_secret_value()) < 10:
            raise ValueError("Webhook secret must be at least 10 characters long.")
        return self

    def get_logging_configuration(self):
        """
        Return a logging-safe configuration dictionary.
        Ensures sensitive keys are not included in logs or outputs.
        """
        return {
            "currency": self.currency,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "debug_mode": self.debug_mode,
        }
