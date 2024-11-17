from typing import Any, Dict

from pydantic import Field, model_validator

from .base import BaseConfig


class PrometheusSettings(BaseConfig):
    """Settings for Prometheus metrics collection."""

    enabled: bool = Field(
        default=False,
        description="Enable or disable Prometheus metrics collection.",
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host address for Prometheus metrics endpoint.",
    )
    port: int = Field(
        default=9090,
        ge=1,
        le=65535,
        description="Port number for Prometheus metrics endpoint.",
    )
    metrics_path: str = Field(
        default="/metrics",
        description="Path for Prometheus metrics endpoint.",
    )
    custom_labels: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom labels for Prometheus metrics.",
    )
    exclude_paths: list[str] = Field(
        default_factory=lambda: [".*admin.*", "/metrics"],
        description="Paths to exclude from metrics collection.",
    )
    restrict_access: bool = Field(
        default=True,
        description="Restrict access to the metrics endpoint.",
    )
    allowed_ips: list[str] = Field(
        default_factory=list,
        description=(
            "List of IPs allowed to access the metrics endpoint "
            "when restrict_access is enabled."
        ),
    )

    # Replace `Config` with `model_config` for Pydantic v2 compatibility
    model_config = {
        "env_prefix": "PROMETHEUS_",
    }

    @model_validator(mode="after")
    def validate_security_settings(self):
        """
        Validate custom_labels, exclude_paths, and network-level security settings.
        """
        # Ensure custom_labels do not expose sensitive information
        sensitive_keys = ["password", "token"]
        if any(
            any(key in label.lower() for key in sensitive_keys)
            for label in self.custom_labels
        ):
            raise ValueError(
                "custom_labels should not contain sensitive keys "
                "like 'password' or 'token'."
            )

        # Ensure exclude_paths properly excludes sensitive paths
        if "/metrics" not in self.exclude_paths:
            raise ValueError(
                "/metrics must be included in exclude_paths to "
                "prevent duplicate collection."
            )

        # Validate IP whitelisting if restrict_access is enabled
        if self.restrict_access and not self.allowed_ips:
            raise ValueError(
                "restrict_access is enabled, but no allowed_ips are defined. "
                "Specify at least one IP address in allowed_ips."
            )
        return self
