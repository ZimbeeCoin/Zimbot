# src/zimbot/core/utils/logger.py

import json
import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from ..config import settings  # Adjusted to use relative import


class JsonFormatter(logging.Formatter):
    """
    Custom logging formatter to output logs in JSON format, including additional context.
    """

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": getattr(record, "service_name", settings.service_name),
            "instance_id": getattr(record, "instance_id", settings.instance_id),
            "environment": getattr(record, "environment", settings.environment),
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
            log_record["message"] = re.sub(
                r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
                "Bearer [REDACTED]",
                log_record["message"],
            )
        return json.dumps(log_record)


class MaskSensitiveFilter(logging.Filter):
    """
    Filters sensitive information from log records.
    """

    def __init__(self):
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        # Example pattern to mask API keys or tokens
        if hasattr(record, "message"):
            record.message = re.sub(
                r"(?i)(apikey|api_key|secret_key|token)\s*=\s*\S+",
                r"\1=****",
                record.message,
            )
        return True


class MetadataFilter(logging.Filter):
    """
    Injects service-level metadata into log records.
    """

    def __init__(self, service_name: str, instance_id: str, environment: str):
        super().__init__()
        self.service_name = service_name
        self.instance_id = instance_id
        self.environment = environment

    def filter(self, record: logging.LogRecord) -> bool:
        record.service_name = self.service_name
        record.instance_id = self.instance_id
        record.environment = self.environment
        return True


def setup_logging(logging_settings: settings.LoggingSettings):
    """
    Configure the logging based on the provided LoggingSettings.
    Supports both plain and structured (JSON) logging.
    """
    logger = logging.getLogger()
    logger.setLevel(logging_settings.log_level)

    # Avoid adding multiple handlers if already configured
    if logger.hasHandlers():
        return

    handlers = []

    # Console Handler
    if logging_settings.log_handlers in ["console", "both"]:
        console_handler = logging.StreamHandler(sys.stdout)
        handlers.append(console_handler)

    # File Handler
    if (
        logging_settings.log_handlers in ["file", "both"]
        and logging_settings.log_file_path
    ):
        file_handler = RotatingFileHandler(
            logging_settings.log_file_path,
            maxBytes=10**6,
            backupCount=5,  # 1MB
        )
        handlers.append(file_handler)

    # Add handlers to the logger
    for handler in handlers:
        if logging_settings.structured:
            formatter = JsonFormatter(logging_settings.log_format)
        else:
            formatter = logging.Formatter(logging_settings.log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Add metadata and sensitive data filters
    metadata_filter = MetadataFilter(
        service_name=settings.service_name,
        instance_id=settings.instance_id,
        environment=settings.environment,
    )
    sensitive_filter = MaskSensitiveFilter()
    logger.addFilter(metadata_filter)
    logger.addFilter(sensitive_filter)


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger with the specified name, configured based on centralized settings.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    setup_logging(settings.logging)
    return logging.getLogger(name)
