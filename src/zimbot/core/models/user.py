# src/zimbot/core/models/user.py

from __future__ import annotations  # Enable forward references for type hints

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr,
    mapped_column,
    relationship,
)

from .audit_log import AuditLog  # Import AuditLog to resolve undefined name
from .base import Base  # Import Base from base.py
from .encrypted_fields import EncryptedString  # Import EncryptedString if needed

if TYPE_CHECKING:
    from .portfolio import Portfolio
    from .refresh_token import RefreshToken
    from .role import Role
    from .user_session import UserSession


@declarative_mixin
class TimestampMixin:
    """
    Mixin to add timestamp fields to models.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


@declarative_mixin
class VersionedMixin:
    """
    Mixin to add versioning to models for optimistic concurrency control.
    """

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    @declared_attr
    def __mapper_args__(cls) -> Any:  # type: ignore
        """
        Mapper arguments for versioning.

        Returns:
            Any: SQLAlchemy mapper arguments dictionary.
        """
        return {"version_id_col": cls.version}


class User(Base, TimestampMixin, VersionedMixin):
    """
    Represents a user in the system.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(EncryptedString(32), nullable=True)
    wallet_address: Mapped[str | None] = mapped_column(
        EncryptedString(42), unique=True, nullable=True
    )
    profile_settings: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    temporary_permissions: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        description="Temporary permissions for the user during sessions",
    )

    # Relationships
    portfolios: Mapped[list[Portfolio]] = relationship(
        "Portfolio",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sessions: Mapped[list[UserSession]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("username", "email", name="uq_users_username_email"),
        Index("ix_users_username_email", "username", "email"),
    )

    # Utility Methods

    def has_role(self, role_name: str) -> bool:
        """
        Check if the user has a specific role.

        Args:
            role_name (str): The name of the role to check.

        Returns:
            bool: True if the user has the role, False otherwise.
        """
        return any(role.name == role_name for role in self.roles)

    def get_active_portfolios(self) -> list[Portfolio]:
        """
        Retrieve all active portfolios for the user.

        Returns:
            List[Portfolio]: A list of active Portfolio instances.
        """
        return [portfolio for portfolio in self.portfolios if not portfolio.disabled]

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username='{self.username}', email='{self.email}', "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )
