# logging_config.py

from pathlib import Path
from typing import List, Optional, Literal

from pydantic import ConfigDict, Field, field_validator
from .base import BaseConfig

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class LoggingSettings(BaseConfig):
    """Settings for application logging."""

    log_level: LogLevel = Field(
        "INFO",
        description="Logging level, e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )
    log_file_path: Optional[str] = Field(
        None,
        description=(
            "File path for log output. If not set, logs will be output to stdout."
        ),
    )
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format.",
    )
    log_handlers: List[str] = Field(
        ["console"],
        description="Logging handlers, e.g., 'console', 'file', 'both'.",
    )
    structured: bool = Field(
        False,
        description="Enable structured (JSON) logging.",
    )

    model_config = ConfigDict(env_prefix="LOGGING_")

    @field_validator("log_level")
    def validate_log_level(cls, value: str) -> str:
        """Validate that the log level is one of the allowed levels."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        value_upper = value.upper()
        if value_upper not in allowed_levels:
            raise ValueError(
                f"Invalid log_level '{value}'. Must be one of {allowed_levels}."
            )
        return value_upper

    @field_validator("log_handlers")
    def validate_log_handlers(cls, value: List[str]) -> List[str]:
        """Validate that the log handlers are among the allowed options."""
        allowed_handlers = {"console", "file", "both"}
        for handler in value:
            if handler.lower() not in allowed_handlers:
                raise ValueError(
                    f"Invalid log_handlers '{handler}'. Must be one of {allowed_handlers}."
                )
        return [handler.lower() for handler in value]

    @field_validator("log_file_path", mode="before")
    def validate_log_file_path(
        cls, value: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """
        Validate that log_file_path is set when log_handlers includes 'file' or 'both'.
        """
        handlers = info.data.get("log_handlers", ["console"])
        if any(handler in {"file", "both"} for handler in handlers):
            if not value:
                raise ValueError(
                    "log_file_path must be set when log_handlers includes 'file' or 'both'."
                )
            log_path = Path(value)
            if not log_path.parent.exists():
                raise ValueError(
                    f"The directory for log_file_path '{value}' does not exist."
                )
            if not log_path.parent.is_dir():
                raise ValueError(
                    f"The path '{value}' is not a valid directory."
                )
        return value
