# src/zimbot/core/models/__init__.py

# Import Base for model definitions
from .audit_log import AuditLog
from .base import Base

# Import utility field classes
from .encrypted_fields import EncryptedString
from .portfolio import Portfolio
from .portfolio_asset import PortfolioAsset
from .refresh_token import RefreshToken
from .role import Role
from .session_role import SessionRole

# Import all models to make them accessible at the package level
from .user import User
from .user_session import UserSession

# Expose only essential classes and Base
__all__ = [
    "Base",
    "User",
    "AuditLog",
    "Portfolio",
    "PortfolioAsset",
    "RefreshToken",
    "Role",
    "SessionRole",
    "UserSession",
    "EncryptedString",
]
