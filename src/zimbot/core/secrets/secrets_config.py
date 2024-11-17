# src/zimbot/core/secrets/secrets_config.py

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from .exceptions import ConfigurationValidationError


@dataclass
class SMTPConfig:
    hostname: str = field(default_factory=lambda: os.getenv("SMTP_HOST", ""))
    port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    username: str = field(default_factory=lambda: os.getenv("SMTP_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    from_email: str = field(default_factory=lambda: os.getenv("SMTP_FROM_EMAIL", ""))
    start_tls: bool = field(
        default_factory=lambda: os.getenv("SMTP_START_TLS", "True").lower()
        in ["true", "1", "yes"]
    )

    def validate(self):
        """Validate SMTP configuration."""
        if not self.hostname:
            raise ConfigurationValidationError("SMTP hostname is required.")
        if not (1 <= self.port <= 65535):
            raise ConfigurationValidationError("SMTP port must be between 1 and 65535.")
        if not self.username:
            raise ConfigurationValidationError("SMTP username is required.")
        if not self.password:
            raise ConfigurationValidationError("SMTP password is required.")
        if not self._is_valid_email(self.from_email):
            raise ConfigurationValidationError("Invalid SMTP from_email format.")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Simple regex for validating an email address."""
        regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.match(regex, email) is not None


@dataclass
class AlertingConfig:
    email_alerts: List[str] = field(
        default_factory=lambda: (
            os.getenv("EMAIL_ALERTS", "").split(",")
            if os.getenv("EMAIL_ALERTS")
            else []
        )
    )
    slack_webhooks: List[str] = field(
        default_factory=lambda: (
            os.getenv("SLACK_WEBHOOKS", "").split(",")
            if os.getenv("SLACK_WEBHOOKS")
            else []
        )
    )
    webhook_urls: List[str] = field(
        default_factory=lambda: (
            os.getenv("WEBHOOK_URLS", "").split(",")
            if os.getenv("WEBHOOK_URLS")
            else []
        )
    )
    smtp_config: SMTPConfig = field(default_factory=SMTPConfig)

    def validate(self):
        """Validate Alerting configuration."""
        for email in self.email_alerts:
            if not self._is_valid_email(email):
                raise ConfigurationValidationError(f"Invalid email format: {email}")
        for webhook in self.slack_webhooks + self.webhook_urls:
            if not self._is_valid_url(webhook):
                raise ConfigurationValidationError(
                    f"Invalid webhook URL format: {webhook}"
                )
        self.smtp_config.validate()

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Simple regex for validating an email address."""
        regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.match(regex, email) is not None

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Simple regex for validating a URL."""
        regex = re.compile(
            r"^(https?|ftp)://"  # http:// or https:// or ftp://
            r"(\S+(:\S*)?@)?"  # user and password
            r"([A-Za-z0-9.-]+)"  # domain
            r"(:\d+)?"  # optional port
            r"(/\S*)?$",  # path
            re.IGNORECASE,
        )
        return re.match(regex, url) is not None


@dataclass
class SecretsManagerConfig:
    use_async: bool = field(
        default_factory=lambda: os.getenv("USE_ASYNC", "False").lower()
        in ["true", "1", "yes"]
    )
    aws_region: Optional[str] = field(default_factory=lambda: os.getenv("AWS_REGION"))
    redis_url: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "300")))
    redis_expiry_seconds: int = field(
        default_factory=lambda: int(os.getenv("REDIS_EXPIRY_SECONDS", "300"))
    )
    encryption_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ENCRYPTION_KEY")
    )
    use_secrets_manager: bool = field(
        default_factory=lambda: os.getenv("USE_SECRETS_MANAGER", "True").lower()
        in ["true", "1", "yes"]
    )
    secret_names: Optional[List[str]] = field(
        default_factory=lambda: (
            os.getenv("SECRET_NAMES", "").split(",")
            if os.getenv("SECRET_NAMES")
            else None
        )
    )
    rotation_interval: int = field(
        default_factory=lambda: int(os.getenv("ROTATION_INTERVAL", "86400"))
    )  # Default to 24 hours
    alerting: AlertingConfig = field(default_factory=AlertingConfig)
    metrics_port: int = field(
        default_factory=lambda: int(os.getenv("METRICS_PORT", "8000"))
    )
    expiry_days: Optional[int] = field(
        default_factory=lambda: (
            int(os.getenv("EXPIRY_DAYS")) if os.getenv("EXPIRY_DAYS") else None
        )
    )
    max_keys: Optional[int] = field(
        default_factory=lambda: (
            int(os.getenv("MAX_KEYS")) if os.getenv("MAX_KEYS") else None
        )
    )
    auto_key_rotation: bool = field(
        default_factory=lambda: os.getenv("AUTO_KEY_ROTATION", "False").lower()
        in ["true", "1", "yes"]
    )
    backup_retention_limit: Optional[int] = field(
        default_factory=lambda: (
            int(os.getenv("BACKUP_RETENTION_LIMIT"))
            if os.getenv("BACKUP_RETENTION_LIMIT")
            else None
        )
    )
    # Additional configurations for retry and circuit breaker
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("SECRETS_MAX_RETRIES", "5"))
    )
    backoff_base: float = field(
        default_factory=lambda: float(os.getenv("SECRETS_BACKOFF_BASE", "0.5"))
    )
    circuit_breaker_failure_threshold: int = field(
        default_factory=lambda: int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    )
    circuit_breaker_recovery_timeout: int = field(
        default_factory=lambda: int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60"))
    )

    def validate(self):
        """Validate SecretsManager configuration."""
        if not self.encryption_key:
            raise ConfigurationValidationError("ENCRYPTION_KEY is required.")
        if self.use_secrets_manager and not self.secret_names:
            raise ConfigurationValidationError(
                "SECRET_NAMES must be provided when USE_SECRETS_MANAGER is True."
            )
        if self.cache_ttl < 0:
            raise ConfigurationValidationError("CACHE_TTL must be non-negative.")
        if self.redis_expiry_seconds < 0:
            raise ConfigurationValidationError(
                "REDIS_EXPIRY_SECONDS must be non-negative."
            )
        if self.rotation_interval <= 0:
            raise ConfigurationValidationError("ROTATION_INTERVAL must be positive.")
        if self.expiry_days is not None and self.expiry_days <= 0:
            raise ConfigurationValidationError("EXPIRY_DAYS must be positive if set.")
        if self.max_keys is not None and self.max_keys <= 0:
            raise ConfigurationValidationError("MAX_KEYS must be positive if set.")
        if self.backup_retention_limit is not None and self.backup_retention_limit <= 0:
            raise ConfigurationValidationError(
                "BACKUP_RETENTION_LIMIT must be positive if set."
            )
        if self.max_retries <= 0:
            raise ConfigurationValidationError("SECRETS_MAX_RETRIES must be positive.")
        if self.backoff_base <= 0:
            raise ConfigurationValidationError("SECRETS_BACKOFF_BASE must be positive.")
        if self.circuit_breaker_failure_threshold <= 0:
            raise ConfigurationValidationError(
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD must be positive."
            )
        if self.circuit_breaker_recovery_timeout <= 0:
            raise ConfigurationValidationError(
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT must be positive."
            )
        self.alerting.validate()
