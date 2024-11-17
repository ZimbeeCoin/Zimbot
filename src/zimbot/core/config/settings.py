# settings.py

from __future__ import annotations  # Enables forward references for type hints

import logging
from typing import Any, Dict, List, Optional, Set

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    Field,
    SecretStr,
    ValidationInfo,
    field_validator,
    model_validator,
    parse_obj_as,
    ConfigDict,
)

# Import sub-settings classes from their respective modules
from .additional_config import AdditionalSettings
from .api_config import APISettings
from .aws_config import AWSSettings
from .celery_config import CelerySettings
from .coinapi_config import CoinAPISettings
from .cors_config import CORSSettings
from .debug_config import DebugSettings
from .jwt_config import JWTSettings
from .livecoinwatch_config import LiveCoinWatchSettings
from .livekit_config import LiveKitSettings
from .logging_config import LoggingSettings
from .ngrok_config import NgrokSettings
from .openai_config import OpenAISettings
from .prometheus_config import PrometheusSettings
from .rate_limit_config import RateLimitSettings
from .redis_config import RedisSettings
from .streaming_config import StreamingConfig
from .stripe_config import StripeSettings
from .telegram_bot_config import TelegramBotSettings

# Configure logger
logger = logging.getLogger(__name__)


class MissingSecretError(Exception):
    """Raised when required secrets are missing."""
    pass


class Settings(BaseSettings):
    """
    Centralized settings that aggregates all configuration modules.
    """

    # Model config using new Pydantic v2 style
    model_config = ConfigDict(
        validate_assignment=True,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow',
        str_strip_whitespace=True,
        populate_by_name=True,
        case_sensitive=False,
        json_schema_extra={
            "title": "Application Settings",
            "description": "Configuration settings for the application"
        }
    )

    # Configuration Modules
    logging: LoggingSettings = Field(default_factory=lambda: LoggingSettings(
        log_level="INFO",
        log_file_path="logs/app.log",
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_handlers=["console"],
        structured=False
    ))
    cors: CORSSettings = Field(default_factory=lambda: CORSSettings(
        allowed_origins=["http://localhost:8000"],
        allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allowed_headers=["*"],
        allow_credentials=True,
        max_age=600,
        expose_headers=[]
    ))
    api: APISettings = Field(default_factory=lambda: APISettings(
        base_url="http://localhost:8000",
        host="0.0.0.0",
        port=8000
    ))
    rate_limit: RateLimitSettings = Field(default_factory=lambda: RateLimitSettings())
    debug: DebugSettings = Field(default_factory=lambda: DebugSettings())
    prometheus: PrometheusSettings = Field(default_factory=lambda: PrometheusSettings())
    redis: RedisSettings = Field(default_factory=lambda: RedisSettings())
    openai: OpenAISettings = Field(default_factory=lambda: OpenAISettings(
        base_url="https://api.openai.com/v1",
        api_key=SecretStr(""),  # Will be overridden by env var
        timeout=30,
        retry_attempts=3
    ))
    livecoinwatch: LiveCoinWatchSettings = Field(default_factory=lambda: LiveCoinWatchSettings())
    coinapi: CoinAPISettings = Field(default_factory=lambda: CoinAPISettings())
    telegram_bot: TelegramBotSettings = Field(default_factory=lambda: TelegramBotSettings())
    jwt: JWTSettings = Field(default_factory=lambda: JWTSettings(
        secret_key=SecretStr(""),  # Will be overridden by env var
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7
    ))
    stripe: StripeSettings = Field(default_factory=lambda: StripeSettings())
    ngrok: NgrokSettings = Field(default_factory=lambda: NgrokSettings())
    streaming: StreamingConfig = Field(default_factory=lambda: StreamingConfig())
    livekit: LiveKitSettings = Field(default_factory=lambda: LiveKitSettings())
    additional: AdditionalSettings = Field(default_factory=lambda: AdditionalSettings())
    aws: AWSSettings = Field(default_factory=lambda: AWSSettings())
    celery: CelerySettings = Field(default_factory=lambda: CelerySettings())

    # API and Server Configuration
    allowed_hosts: Set[str] = Field(
        default_factory=lambda: {"localhost", "127.0.0.1"},
        description="List of allowed hosts",
    )
    allowed_origins: List[AnyHttpUrl] = Field(
        default_factory=lambda: ["http://localhost", "http://localhost:8000"],
        description="List of allowed CORS origins",
    )
    valid_api_keys: List[str] = Field(
        default_factory=list, description="List of valid API keys"
    )
    api_base_url: AnyHttpUrl = Field(
        default="http://localhost:8000", description="Base URL for the API"
    )
    concurrency_limit: int = Field(
        default=4, description="Number of worker processes"
    )

    # Security Settings
    encryption_key: Optional[SecretStr] = Field(
        None,
        alias="ENCRYPTION_KEY",
        description="Encryption key for security",
    )
    use_secrets_manager: bool = Field(
        default=False,
        alias="USE_SECRETS_MANAGER",
        description="Toggle to use AWS Secrets Manager",
    )

    # Redis Configuration
    redis_enabled: bool = Field(
        default=False, description="Enable Redis for caching"
    )
    redis_expiry_seconds: int = Field(
        default=600,
        alias="REDIS_EXPIRY_SECONDS",
        description="Expiry time for Redis cache in seconds",
    )

    # SMTP Configuration
    smtp_host: str = Field(
        ...,  # Required field
        alias="SMTP_HOST",
        description="SMTP server hostname"
    )
    smtp_port: int = Field(
        ...,  # Required field
        alias="SMTP_PORT",
        description="SMTP server port"
    )
    smtp_username: str = Field(
        ...,  # Required field
        alias="SMTP_USERNAME",
        description="SMTP username"
    )
    smtp_password: SecretStr = Field(
        ...,  # Required field
        alias="SMTP_PASSWORD",
        description="SMTP password"
    )
    smtp_from_email: EmailStr = Field(
        ...,  # Required field
        alias="SMTP_FROM_EMAIL",
        description="SMTP from email address"
    )
    smtp_start_tls: bool = Field(
        default=True, alias="SMTP_START_TLS", description="Enable STARTTLS for SMTP"
    )

    # Notification Settings
    alert_emails: List[EmailStr] = Field(
        default_factory=list,
        alias="ALERT_EMAILS",
        description="List of alert email addresses",
    )
    alerting_slack_webhooks: List[AnyHttpUrl] = Field(
        default_factory=list,
        alias="ADDITIONAL_SLACK_WEBHOOKS",
        description=(
            "List of Slack webhook URLs for sending alerts."
        )
    )
    alerting_generic_webhooks: List[AnyHttpUrl] = Field(
        default_factory=list,
        alias="ADDITIONAL_GENERIC_WEBHOOKS",
        description=(
            "List of generic webhook URLs for sending alerts."
        )
    )

    # Cache Configuration
    cache_ttl: int = Field(
        default=300, alias="CACHE_TTL", description="Cache time-to-live in seconds"
    )

    # Monitoring
    sentry_dsn: Optional[SecretStr] = Field(
        default=None, alias="SENTRY_DSN", description="Sentry DSN for error tracking"
    )

    # Application Metadata
    service_name: str = Field(
        default="RoboRiches AI", description="Service name for logging"
    )
    instance_id: str = Field(
        default="instance_1", description="Unique instance identifier"
    )
    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
        description="Application environment",
    )
    version: Optional[str] = Field(
        default=None, alias="VERSION", description="Application version"
    )

    # OpenTelemetry Configuration
    opentelemetry_endpoint: AnyHttpUrl = Field(
        default="http://localhost:4317",
        alias="OPENTELEMETRY_ENDPOINT",
        description="OpenTelemetry endpoint URL",
    )
    opentelemetry_insecure: bool = Field(
        default=True,
        alias="OPENTELEMETRY_INSECURE",
        description="Whether to use insecure connection for OpenTelemetry",
    )

    # Prometheus Custom Labels
    custom_labels: Dict[str, Any] = Field(
        default_factory=dict,
        alias="PROMETHEUS_CUSTOM_LABELS",
        description="Custom labels for Prometheus metrics",
    )

    # Validators
    @field_validator("alert_emails", mode='before')
    @classmethod
    def split_alert_emails(cls, value: Any) -> List[EmailStr]:
        """
        Split comma-separated string into a list of EmailStr.
        """
        if isinstance(value, str):
            return [
                EmailStr(email.strip()) 
                for email in value.split(",") 
                if email.strip()
            ]
        return value

    @field_validator("alerting_slack_webhooks", mode='before')
    @classmethod
    def split_alerting_slack_webhooks(cls, value: Any) -> List[AnyHttpUrl]:
        """
        Split comma-separated string into a list of AnyHttpUrl.
        """
        if isinstance(value, str):
            return [
                AnyHttpUrl(url.strip()) 
                for url in value.split(",") 
                if url.strip()
            ]
        return value

    @field_validator("alerting_generic_webhooks", mode='before')
    @classmethod
    def split_alerting_generic_webhooks(cls, value: Any) -> List[AnyHttpUrl]:
        """
        Split comma-separated string into a list of AnyHttpUrl.
        """
        if isinstance(value, str):
            return [
                AnyHttpUrl(url.strip()) 
                for url in value.split(",") 
                if url.strip()
            ]
        return value

    @field_validator("environment", mode='after')
    @classmethod
    def ensure_environment_lowercase(cls, value: str) -> str:
        return value.lower()

    @field_validator("allowed_hosts", mode='before')
    @classmethod
    def ensure_allowed_hosts_set(cls, value: Any) -> Set[str]:
        if isinstance(value, str):
            return {host.strip() for host in value.split(",") if host.strip()}
        return value

    @field_validator("allowed_origins", mode='before')
    @classmethod
    def ensure_allowed_origins_list(cls, value: Any) -> List[AnyHttpUrl]:
        if isinstance(value, str):
            try:
                return parse_obj_as(
                    List[AnyHttpUrl],
                    [url.strip() for url in value.split(",") if url.strip()]
                )
            except Exception as e:
                raise ValueError("Invalid URL in allowed_origins.") from e
        return value

    @model_validator(mode='after')
    def validate_required_env_variables(self) -> 'Settings':
        required_vars = {
            "ENCRYPTION_KEY": self.encryption_key,
            "SMTP_HOST": self.smtp_host,
            "SMTP_PORT": self.smtp_port,
            "SMTP_USERNAME": self.smtp_username,
            "SMTP_PASSWORD": self.smtp_password,
            "SMTP_FROM_EMAIL": self.smtp_from_email,
            "JWT_SECRET_KEY": self.jwt.secret_key,
            "OPENAI_API_KEY": self.openai.api_key,
            "COINAPI_API_KEY": self.coinapi.api_key,
            # Add other required environment variables here
        }
        
        if missing := [k for k, v in required_vars.items() if not v]:
            raise MissingSecretError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        return self

    @model_validator(mode='after')
    def log_env_variables(self) -> 'Settings':
        """
        Log environment variables, excluding sensitive information.
        """
        if self.environment == "development":
            safe_values = {
                k: str(v) for k, v in self.model_dump().items()
                if not any(sensitive in k.lower() 
                          for sensitive in ["password", "key", "secret", "token"])
            }
            logger.debug(f"Loaded Environment Variables: {safe_values}")
        return self

    def get_debug_mode(self) -> bool:
        """Helper method to determine if debug mode is enabled."""
        return self.environment.lower() == "development"

    # Additional helper methods can be added here as needed


# Instantiate Settings
settings: Settings = Settings()
