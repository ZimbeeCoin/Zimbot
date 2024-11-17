# src/core/secrets/error_handling.py

"""
Centralized error handling utilities for AWS ClientError exceptions and other errors.
"""

import asyncio
from typing import Any, Dict, Optional

import sentry_sdk
from botocore.exceptions import ClientError

from .alerting import Alerting
from .exceptions import (
    MissingSecretError,
    NonRetryableError,
    RetryableError,
    SecurityError,
)
from .secrets_logger import get_logger

# Get the centralized logger
logger = get_logger(__name__)


def handle_error(
    error: Exception,
    message: str,
    logger_instance,
    alerting: Optional[Alerting] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Centralized error handling function.

    Args:
        error (Exception): The exception that occurred.
        message (str): Custom error message for logging and alerting.
        logger_instance: The logger instance to use.
        alerting (Optional[Alerting]): Alerting utility instance.
        metadata (Optional[Dict[str, Any]]): Additional metadata for logging and alerting.

    Raises:
        Exception: Reraises the original exception.
    """
    error_metadata = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if metadata:
        error_metadata.update(metadata)

    # Log the error with detailed metadata
    logger_instance.error(message, extra={"metadata": error_metadata})

    # Capture exception in Sentry with metadata
    sentry_sdk.capture_exception(error)

    # Send alert if alerting is configured
    if alerting:
        alert_message = f"{message}\nMetadata: {error_metadata}"
        if asyncio.iscoroutinefunction(alerting.send_alert):
            asyncio.create_task(alerting.send_alert(alert_message))
        else:
            alerting.send_alert(alert_message)


def categorize_client_error(error: ClientError) -> Exception:
    """
    Categorize AWS ClientError into finer-grained error categories.

    Args:
        error (ClientError): The exception raised by AWS SDK.

    Returns:
        Exception: A more specific exception based on the error code.
    """
    error_code = error.response.get("Error", {}).get("Code", "Unknown")
    if error_code in {"InternalServiceErrorException", "ThrottlingException"}:
        return RetryableError(f"AWS service error: {error_code}")
    elif error_code in {"InvalidParameterException", "InvalidRequestException"}:
        return NonRetryableError(f"AWS client error: {error_code}")
    elif error_code == "AccessDeniedException":
        return SecurityError(f"AWS access denied: {error_code}")
    elif error_code == "ResourceNotFoundException":
        return MissingSecretError("Secret not found.")
    else:
        return NonRetryableError(f"Unhandled AWS error: {error_code}")


def extract_error_metadata(error: Exception) -> Dict[str, Any]:
    """
    Extract metadata from an exception for logging and alerting.

    Args:
        error (Exception): The exception to extract metadata from.

    Returns:
        Dict[str, Any]: A dictionary containing error metadata.
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }


async def handle_client_error_async(
    error: ClientError,
    secret_name: str,
    alerting: Optional[Alerting] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Handle AWS ClientError exceptions in async context.

    Args:
        error (ClientError): The exception raised by AWS SDK.
        secret_name (str): The name of the secret being retrieved.
        alerting (Optional[Alerting]): Alerting utility instance.
        metadata (Optional[Dict[str, Any]]): Additional metadata for logging and alerting.

    Raises:
        Exception: A more specific exception based on the error code.
    """
    categorized_error = categorize_client_error(error)
    error_metadata = extract_error_metadata(categorized_error)
    if metadata:
        error_metadata.update(metadata)
    error_metadata["secret_name"] = secret_name

    message = f"Error retrieving secret '{secret_name}': {error_metadata['error_type']}"

    # Use the centralized error handler
    handle_error(
        error=categorized_error,
        message=message,
        logger_instance=logger,
        alerting=alerting,
        metadata=error_metadata,
    )

    raise categorized_error


def handle_client_error_sync(
    error: ClientError,
    secret_name: str,
    alerting: Optional[Alerting] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Handle AWS ClientError exceptions in sync context.

    Args:
        error (ClientError): The exception raised by AWS SDK.
        secret_name (str): The name of the secret being retrieved.
        alerting (Optional[Alerting]): Alerting utility instance.
        metadata (Optional[Dict[str, Any]]): Additional metadata for logging and alerting.

    Raises:
        Exception: A more specific exception based on the error code.
    """
    categorized_error = categorize_client_error(error)
    error_metadata = extract_error_metadata(categorized_error)
    if metadata:
        error_metadata.update(metadata)
    error_metadata["secret_name"] = secret_name

    message = f"Error retrieving secret '{secret_name}': {error_metadata['error_type']}"

    # Use the centralized error handler
    handle_error(
        error=categorized_error,
        message=message,
        logger_instance=logger,
        alerting=alerting,
        metadata=error_metadata,
    )

    raise categorized_error
