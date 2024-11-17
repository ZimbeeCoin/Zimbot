import json
import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from .filters import MaskSensitiveFilter, MetadataFilter
from .logging_config import LoggingSettings


class JsonFormatter(logging.Formatter):
    """
    Custom logging formatter to output logs in JSON format.
    """
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": getattr(record, "service_name", "UnknownService"),
            "instance_id": getattr(record, "instance_id", "UnknownInstance"),
            "environment": getattr(record, "environment", "unknown"),
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        # Include exception information if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        # Mask sensitive information
        if "Bearer " in log_record["message"]:
            pattern = r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"
            replacement = "Bearer [REDACTED]"
            log_record["message"] = re.sub(pattern, replacement, log_record["message"])
        # Include trace ID if present
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = getattr(record, "trace_id", "unknown")
        return json.dumps(log_record)


def setup_logging(
    logging_settings: LoggingSettings,
    service_name: str,
    instance_id: str,
    environment: str,
):
    """
    Configure the logging based on the provided LoggingSettings.
    Supports both plain and structured (JSON) logging.
    """
    logger = logging.getLogger()
    logger.setLevel(logging_settings.log_level)

    # Avoid adding multiple handlers if already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    handlers = []
    # Console Handler
    if logging_settings.log_handlers in {"console", "both"}:
        console_handler = logging.StreamHandler(sys.stdout)
        handlers.append(console_handler)

    # File Handler
    if logging_settings.log_handlers in {"file", "both"}:
        if not logging_settings.log_file_path:
            raise ValueError(
                "log_file_path must be a non-empty string for file logging"
            )
        file_handler = RotatingFileHandler(
            logging_settings.log_file_path,
            maxBytes=10**6,  # 1MB
            backupCount=5,
        )
        handlers.append(file_handler)

    # Create formatter outside the loop as it's the same for all handlers
    default_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_format = logging_settings.log_format or default_format
    formatter = (
        JsonFormatter(log_format)
        if logging_settings.structured
        else logging.Formatter(log_format)
    )

    # Add handlers to the logger
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Add metadata and sensitive data filters
    metadata_filter = MetadataFilter(
        service_name=service_name,
        instance_id=instance_id,
        environment=environment,
    )
    sensitive_filter = MaskSensitiveFilter()
    logger.addFilter(metadata_filter)
    logger.addFilter(sensitive_filter)


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a centrally configured logger by name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
