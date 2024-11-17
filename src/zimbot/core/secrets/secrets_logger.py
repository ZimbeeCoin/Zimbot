# src/core/secrets/secrets_logger.py

"""
Module for configuring custom logging with sensitive data masking and integrating with Sentry.
"""

import logging
import os
import re
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Patterns to identify sensitive data (e.g., API keys, tokens)
SENSITIVE_PATTERNS = [
    re.compile(r"(api_key\s*=\s*)([^\s]+)", re.IGNORECASE),
    re.compile(r"(access_token\s*=\s*)([^\s]+)", re.IGNORECASE),
    re.compile(r"(secret\s*=\s*)([^\s]+)", re.IGNORECASE),
    re.compile(r"(password\s*=\s*)([^\s]+)", re.IGNORECASE),
    # Add more patterns as needed
]


def sanitize_log_message(message: str) -> str:
    """
    Sanitize log messages by masking sensitive information.

    Args:
        message (str): The original log message.

    Returns:
        str: The sanitized log message.
    """
    for pattern in SENSITIVE_PATTERNS:
        message = pattern.sub(r"\1******", message)
    return message


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to sanitize log records before they are emitted.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        elif isinstance(record.msg, dict):
            # If the message is a dictionary, sanitize its string representation
            record.msg = sanitize_log_message(str(record.msg))
        return True


def configure_logging():
    """
    Configure logging with Sentry integration and sensitive data masking.
    """
    # Configure Sentry
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors and above as events
    )
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
    )

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(os.getenv("LOGGING_LEVEL", "INFO").upper())

    # Create console handler with a standard format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger.level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the sensitive data filter to the handler
    console_handler.addFilter(SensitiveDataFilter())

    # Remove any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add the handler to the logger
    logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)


# Initialize logging configuration upon module import
configure_logging()
