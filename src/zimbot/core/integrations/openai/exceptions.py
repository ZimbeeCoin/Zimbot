# src/core/integrations/exceptions.py


class InvalidCredentialsError(Exception):
    """Raised when user credentials are invalid."""


class TokenBlacklistedError(Exception):
    """Raised when a token is blacklisted."""


class TokenRevokedError(Exception):
    """Raised when a token has been revoked."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user that already exists."""


class UserNotFoundError(Exception):
    """Raised when a user is not found."""


class MFASetupError(Exception):
    """Raised when MFA setup fails."""


class MFAValidationError(Exception):
    """Raised when MFA token validation fails."""
