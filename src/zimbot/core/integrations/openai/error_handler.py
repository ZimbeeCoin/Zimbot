# src/core/integrations/openai/error_handler.py

import logging
from typing import Any, Dict, Optional

import sentry_sdk

from .types import APIError, AuthenticationError, OpenAIError, RateLimitError

logger = logging.getLogger(__name__)


class OpenAIErrorHandler:
    """Enhanced error handler for OpenAI operations"""

    @staticmethod
    async def handle_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> bool:
        """
        Handle OpenAI errors with contextual logging and Sentry integration.
        Returns True if the error is recoverable.

        Args:
            error (Exception): The exception to handle.
            context (Optional[Dict[str, Any]]): Additional context for logging.
            retry_count (int): The current retry attempt count.

        Returns:
            bool: True if the error is recoverable and can be retried, False otherwise.
        """
        context = context or {}

        if isinstance(error, RateLimitError):
            logger.warning(
                f"Rate limit exceeded (retry {retry_count}). Context: {context}",
                extra={"error_context": context},
            )
            sentry_sdk.capture_exception(
                error, extras={"retry_count": retry_count, **context}
            )
            return True  # Recoverable with retry

        elif isinstance(error, AuthenticationError):
            logger.error(
                f"Authentication failed. Context: {context}",
                extra={"error_context": context},
            )
            sentry_sdk.capture_exception(
                error, extras={"auth_failure": True, **context}
            )
            return False  # Not recoverable

        elif isinstance(error, APIError):
            if error.status_code in {503, 504}:  # Service unavailable
                logger.warning(
                    f"OpenAI service temporarily unavailable (retry {retry_count}). Context: {context}",
                    extra={"error_context": context},
                )
                sentry_sdk.capture_exception(
                    error, extras={"status_code": error.status_code, **context}
                )
                return True  # Recoverable with retry

            logger.error(
                f"OpenAI API error: {error}. Context: {context}",
                extra={
                    "error_context": context,
                    "status_code": error.status_code,
                },
            )
            sentry_sdk.capture_exception(
                error, extras={"status_code": error.status_code, **context}
            )
            return False  # Not recoverable

        else:
            logger.error(
                f"Unexpected error: {error}. Context: {context}",
                extra={"error_context": context},
            )
            sentry_sdk.capture_exception(
                error, extras={"unexpected_error": True, **context}
            )
            return False  # Not recoverable

    @staticmethod
    def format_error_response(error: Exception) -> Dict[str, Any]:
        """
        Format error response for API endpoints based on the exception type.

        Args:
            error (Exception): The exception to format.

        Returns:
            Dict[str, Any]: The formatted error response.
        """
        if isinstance(error, RateLimitError):
            return {
                "error": "rate_limit_exceeded",
                "message": "API rate limit exceeded. Please try again later.",
                "retry_after": 60,  # Default retry after 60 seconds
            }

        elif isinstance(error, AuthenticationError):
            return {
                "error": "authentication_failed",
                "message": "Failed to authenticate with OpenAI API.",
            }

        elif isinstance(error, APIError):
            return {
                "error": "api_error",
                "message": str(error),
                "status_code": error.status_code,
            }

        return {
            "error": "internal_error",
            "message": "An unexpected error occurred.",
        }
