# src/core/secrets/exceptions.py

"""
Custom exception classes for Secrets Management.
Provides a single base exception class for all secrets-related errors.
"""


class SecretsManagerError(Exception):
    """Base exception class for all SecretsManager errors."""

    def __init__(self, message: str, **context):
        """
        Initialize a SecretsManagerError with a message and optional context.

        Args:
            message (str): A descriptive error message.
            context (dict): Additional context information (e.g., operation, secret name).
        """
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self):
        context_str = ", ".join(
            f"{key}='{value}'" for key, value in self.context.items()
        )
        return f"{self.message} ({context_str})" if context_str else self.message


class MissingSecretError(SecretsManagerError):
    """Raised when a requested secret is missing."""

    def __init__(self, secret_name: str):
        super().__init__(f"Secret '{secret_name}' is missing.", secret_name=secret_name)


class MaxRetriesExceededError(SecretsManagerError):
    """Raised when the maximum number of retries is exceeded."""

    def __init__(self, operation: str, retries: int):
        message = f"Maximum retry attempts exceeded for operation '{operation}'."
        super().__init__(message, operation=operation, retries=retries)


class ConfigurationValidationError(SecretsManagerError):
    """Raised when configuration validation fails."""

    def __init__(self, message: str = "Configuration validation failed."):
        super().__init__(message)


class EncryptionError(SecretsManagerError):
    """Raised when encryption fails."""

    def __init__(self, message: str = "An error occurred during encryption."):
        super().__init__(message)


class DecryptionError(SecretsManagerError):
    """Raised when decryption fails."""

    def __init__(self, message: str = "An error occurred during decryption."):
        super().__init__(message)


class CachingError(SecretsManagerError):
    """Raised when caching operations fail."""

    def __init__(self, message: str = "An error occurred during caching operations."):
        super().__init__(message)


class KeyRotationError(SecretsManagerError):
    """Raised when key rotation fails."""

    def __init__(self, message: str = "Failed to rotate encryption keys."):
        super().__init__(message)
