# src/zimbot/core/integrations/exceptions/exceptions.py

from typing import Optional


class IntegrationError(Exception):
    """Base exception for integration-related errors."""

    def __init__(self, message: str, code: Optional[str] = None):
        """
        Initialize the IntegrationError.

        Args:
            message (str): Description of the error.
            code (Optional[str]): Optional error code for categorization.
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


# New exception classes used in auth_service.py


class InvalidCredentialsError(IntegrationError):
    """Raised when invalid credentials are provided."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, code="INVALID_CREDENTIALS")


class MFASetupError(IntegrationError):
    """Raised when MFA setup fails."""

    def __init__(self, message: str = "MFA setup failed"):
        super().__init__(message, code="MFA_SETUP_ERROR")


class MFAValidationError(IntegrationError):
    """Raised when MFA validation fails."""

    def __init__(self, message: str = "MFA validation failed"):
        super().__init__(message, code="MFA_VALIDATION_ERROR")


class TokenBlacklistedError(IntegrationError):
    """Raised when a token is blacklisted."""

    def __init__(self, message: str = "Token is blacklisted"):
        super().__init__(message, code="TOKEN_BLACKLISTED")


class TokenRevokedError(IntegrationError):
    """Raised when a token is revoked."""

    def __init__(self, message: str = "Token is revoked"):
        super().__init__(message, code="TOKEN_REVOKED")


class UserAlreadyExistsError(IntegrationError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str = "User already exists"):
        super().__init__(message, code="USER_ALREADY_EXISTS")


# Existing exceptions


class AuthenticationError(IntegrationError):
    """Raised when authentication fails with an integration."""

    def __init__(self, message: str, service: str):
        """
        Initialize the AuthenticationError.

        Args:
            message (str): Description of the authentication failure.
            service (str): Name of the service where authentication failed.
        """
        self.service = service
        super().__init__(
            f"{service} authentication failed: {message}", code="AUTH_ERROR"
        )


class RateLimitError(IntegrationError):
    """Raised when rate limits are exceeded."""

    def __init__(self, service: str, limit: str, reset_at: Optional[int] = None):
        """
        Initialize the RateLimitError.

        Args:
            service (str): Name of the service where rate limit was exceeded.
            limit (str): Description of the rate limit.
            reset_at (Optional[int]): Timestamp when the rate limit resets.
        """
        self.reset_at = reset_at
        message = (
            f"{service} rate limit exceeded ({limit}). Reset at: {reset_at}"
            if reset_at
            else f"{service} rate limit exceeded ({limit})."
        )
        super().__init__(message, code="RATE_LIMIT")


class DataFetchError(IntegrationError):
    """Raised when data fetching fails."""

    def __init__(self, source: str, detail: str):
        """
        Initialize the DataFetchError.

        Args:
            source (str): Source from which data fetching failed.
            detail (str): Detailed description of the failure.
        """
        super().__init__(
            f"Failed to fetch data from {source}: {detail}", code="DATA_FETCH"
        )


class ServiceUnavailableError(IntegrationError):
    """Raised when a service is unavailable."""

    def __init__(self, service: str, detail: str):
        """
        Initialize the ServiceUnavailableError.

        Args:
            service (str): Name of the unavailable service.
            detail (str): Detailed description of the unavailability.
        """
        super().__init__(
            f"{service} service unavailable: {detail}", code="SERVICE_UNAVAILABLE"
        )


class WebhookError(IntegrationError):
    """Raised when webhook operations fail."""

    def __init__(self, service: str, operation: str, detail: str):
        """
        Initialize the WebhookError.

        Args:
            service (str): Name of the service handling the webhook.
            operation (str): The webhook operation that failed.
            detail (str): Detailed description of the failure.
        """
        super().__init__(
            f"{service} webhook {operation} failed: {detail}", code="WEBHOOK_ERROR"
        )
