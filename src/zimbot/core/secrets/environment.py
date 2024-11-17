# src/zimbot/core/secrets/environment.py

"""
Module for handling secret retrieval, supporting environment variables and AWS Secrets Manager.
"""

import json
import logging
import os
import re
from functools import lru_cache
from typing import Optional

from ..config.aws_config import aws_settings
from .aws_client_manager import AWSClientManager  # Ensure correct import path
from .exceptions import MissingSecretError


# Configure structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "EnvironmentSecretsManager",
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        return json.dumps(log_record)


def configure_logging():
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)


configure_logging()
logger = logging.getLogger(__name__)


class EnvironmentSecretsManager:
    """
    Handles retrieval of secrets from environment variables or AWS Secrets Manager based on configuration.
    """

    def __init__(self, aws_client_manager: Optional[AWSClientManager] = None):
        """
        Initialize the EnvironmentSecretsManager.

        Args:
            aws_client_manager (Optional[AWSClientManager]): AWSClientManager instance for accessing AWS Secrets Manager.
        """
        self.aws_client_manager = aws_client_manager

    def validate_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Validate the format of the retrieved secret.

        Args:
            secret_name (str): The name of the secret.
            secret_value (str): The value of the secret.

        Returns:
            bool: True if the secret is valid, False otherwise.
        """
        if secret_name.endswith("_API_KEY"):
            return bool(re.fullmatch(r"[A-Za-z0-9]{32}", secret_value))
        # Add more validation rules as needed
        return True

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> str:
        """
        Retrieve a secret from AWS Secrets Manager or environment, with an optional fallback.

        Args:
            secret_name (str): The name of the secret to retrieve.
            default (Optional[str]): An optional default value to return if the secret is not found.

        Returns:
            str: The secret value.

        Raises:
            MissingSecretError: If the secret is not found in both AWS Secrets Manager and environment variables.
            ValueError: If the secret fails validation.
        """
        secret = None

        if aws_settings.is_aws_enabled():
            if not self.aws_client_manager:
                logger.error("AWSClientManager is not initialized.")
                if default is not None:
                    logger.debug(f"Using default value for secret '{secret_name}'.")
                    secret = default
                else:
                    raise MissingSecretError(secret_name)
            else:
                try:
                    secret = self.aws_client_manager.get_secret_sync(secret_name)
                    if secret:
                        logger.debug(
                            f"Retrieved secret '{secret_name}' from AWS Secrets Manager."
                        )
                    else:
                        logger.warning(
                            f"Secret '{secret_name}' not found in AWS Secrets Manager."
                        )
                except Exception as e:
                    logger.error(
                        f"Error retrieving secret '{secret_name}' from AWS Secrets Manager: {e}"
                    )

        if not secret:
            # Fallback to environment variable if AWS retrieval fails or is disabled
            secret = os.getenv(secret_name, default)
            if secret:
                source = (
                    "environment variables"
                    if aws_settings.is_aws_enabled()
                    else "default settings"
                )
                logger.debug(f"Retrieved secret '{secret_name}' from {source}.")

        if not secret:
            # Final fallback if secret is not found
            logger.error(
                f"Secret '{secret_name}' is missing in both AWS Secrets Manager and environment variables."
            )
            raise MissingSecretError(secret_name)

        # Validate the secret
        if not self.validate_secret(secret_name, secret):
            logger.error(f"Validation failed for secret '{secret_name}'.")
            raise ValueError(f"Invalid format for secret '{secret_name}'.")

        return secret
