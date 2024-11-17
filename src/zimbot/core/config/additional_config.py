from typing import Any, List, Optional
from urllib.parse import urlparse

from email_validator import EmailNotValidError, validate_email
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

from .aws_config import aws_settings


class AdditionalSettings(BaseModel):
    """Additional non-grouped settings for application configuration.

    This model follows Pydantic v2 standards and includes comprehensive validation
    for all fields including emails, URLs, and webhook endpoints.
    """
    model_config = ConfigDict(
        frozen=True,  # Make the model immutable
        strict=True,  # Enforce strict type checking
        validate_assignment=True,  # Validate values on assignment
        populate_by_name=True,  # Allow population by alias
        str_strip_whitespace=True,  # Strip whitespace from string values
        json_schema_extra={
            "examples": [
                {
                    "service_name": "RoboRiches AI",
                    "environment": "development",
                    "concurrency_limit": 10,
                }
            ]
        }
    )

    # General Configuration
    valid_api_keys: List[str] = Field(
        default_factory=list,
        description="List of valid API keys for authentication.",
        min_length=0,
        json_schema_extra={"example": ["key1", "key2"]}
    )

    shutdown_timeout: int = Field(
        30,
        ge=10,
        description="Timeout in seconds for application shutdown.",
        json_schema_extra={"example": 30}
    )

    concurrency_limit: int = Field(
        10,
        ge=1,
        description="Concurrency limit for batch processing operations.",
        json_schema_extra={"example": 10}
    )

    service_name: str = Field(
        "RoboRiches AI",
        min_length=1,
        max_length=100,
        description="Name of the service for logging purposes.",
        json_schema_extra={"example": "RoboRiches AI"}
    )

    instance_id: str = Field(
        "instance_1",
        min_length=1,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Unique identifier for the service instance.",
        json_schema_extra={"example": "instance_1"}
    )

    environment: str = Field(
        "development",
        pattern="^(development|staging|production)$",
        description="Application environment (e.g., development, staging, production).",
        json_schema_extra={"example": "development"}
    )

    sentry_dsn: Optional[SecretStr] = Field(
        None,
        description="DSN for Sentry error tracking.",
        json_schema_extra={"example": "https://...@sentry.io/..."}
    )

    # Alerting Configuration
    alerting_emails: List[EmailStr] = Field(
        default_factory=list,
        alias="ADDITIONAL_ALERTING_EMAILS",
        description="Email addresses to send alerts to.",
        json_schema_extra={"example": ["alerts@example.com"]}
    )

    alerting_slack_webhooks: List[AnyHttpUrl] = Field(
        default_factory=list,
        alias="ADDITIONAL_SLACK_WEBHOOKS",
        description="Slack webhook URLs for sending alerts.",
        json_schema_extra={"example": ["https://hooks.slack.com/services/..."]}
    )

    alerting_generic_webhooks: List[AnyHttpUrl] = Field(
        default_factory=list,
        alias="ADDITIONAL_GENERIC_WEBHOOKS",
        description="Generic webhook URLs for sending alerts.",
        json_schema_extra={"example": ["https://api.example.com/webhook"]}
    )

    # Security Configuration
    encryption_key: Optional[SecretStr] = Field(
        None,
        alias="ADDITIONAL_ENCRYPTION_KEY",
        description="Encryption key for encrypting secrets before caching.",
        json_schema_extra={"example": "your-encryption-key"}
    )

    # Caching Configuration
    cache_ttl: int = Field(
        3600,
        ge=60,
        alias="ADDITIONAL_CACHE_TTL",
        description="Time-to-live for cached secrets in seconds.",
        json_schema_extra={"example": 3600}
    )

    @field_validator("alerting_emails", mode="before")
    @classmethod
    def validate_alerting_emails(cls, value: Any) -> List[str]:
        """Validate and normalize email addresses."""
        if isinstance(value, str):
            emails = [email.strip() for email in value.split(",") if email.strip()]
        elif isinstance(value, (list, tuple)):
            emails = [str(email).strip() for email in value if str(email).strip()]
        else:
            raise ValueError("Invalid email format. Expected string or list of strings.")

        validated_emails = []
        for email in emails:
            try:
                valid = validate_email(email, check_deliverability=False)
                validated_emails.append(valid.normalized)
            except EmailNotValidError as e:
                raise ValueError(f"Invalid email address: {email}") from e

        return validated_emails

    @field_validator("alerting_slack_webhooks", "alerting_generic_webhooks", mode="before")
    @classmethod
    def validate_webhook_urls(cls, value: Any, info: Any) -> List[str]:
        """Validate webhook URLs."""
        if isinstance(value, str):
            urls = [url.strip() for url in value.split(",") if url.strip()]
        elif isinstance(value, (list, tuple)):
            urls = [str(url).strip() for url in value if str(url).strip()]
        else:
            raise ValueError("Invalid URL format. Expected string or list of strings.")

        validated_urls = []
        for url in urls:
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError(f"Invalid URL format: {url}")
                if (info.field_name == "alerting_slack_webhooks"
                        and not url.startswith("https://hooks.slack.com/")):
                    raise ValueError(f"Invalid Slack webhook URL: {url}")
                validated_urls.append(url)
            except Exception as e:
                raise ValueError(f"Invalid URL: {url}") from e

        return validated_urls

    @model_validator(mode="after")
    def validate_model(self) -> "AdditionalSettings":
        """Perform cross-field validation after individual field validation."""
        if self.environment == "production":
            if not self.sentry_dsn:
                raise ValueError("Sentry DSN is required in production environment")
            if not self.alerting_emails:
                raise ValueError("Alert emails are required in production environment")
            if not self.encryption_key:
                raise ValueError("Encryption key is required in production environment")

        return self

    @property
    def use_secrets_manager(self) -> bool:
        """Read-only property indicating whether AWS Secrets Manager should be used."""
        return aws_settings.is_aws_enabled()

    @classmethod
    def get_settings(
        cls,
        *,  # Force keyword arguments
        shutdown_timeout: int = 30,
        concurrency_limit: int = 10,
        service_name: str = "RoboRiches AI",
        instance_id: str = "instance_1",
        environment: str = "development",
        sentry_dsn: Optional[str] = None,
        encryption_key: Optional[str] = None,
        cache_ttl: int = 3600,
    ) -> "AdditionalSettings":
        """Get instance of settings.

        Args:
            shutdown_timeout: Timeout in seconds for application shutdown
            concurrency_limit: Concurrency limit for batch processing
            service_name: Name of the service for logging
            instance_id: Unique identifier for the service instance
            environment: Application environment
            sentry_dsn: DSN for Sentry error tracking
            encryption_key: Encryption key for secrets
            cache_ttl: Time-to-live for cached secrets

        Returns:
            AdditionalSettings: Settings instance
        """
        return cls(
            shutdown_timeout=shutdown_timeout,
            concurrency_limit=concurrency_limit,
            service_name=service_name,
            instance_id=instance_id,
            environment=environment,
            sentry_dsn=SecretStr(sentry_dsn) if sentry_dsn else None,
            ADDITIONAL_ENCRYPTION_KEY=SecretStr(encryption_key) if encryption_key else None,
            ADDITIONAL_CACHE_TTL=cache_ttl,
        )


# Create a singleton instance
settings = AdditionalSettings.get_settings()
