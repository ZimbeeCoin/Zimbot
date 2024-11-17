# src/zimbot/core/models/user_session.py

from __future__ import annotations  # Enable forward references for type hints

from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .role import Role  # Import Role from role.py
from .session_role import SessionRole  # Ensure this model is defined similarly
from .user import TimestampMixin, User, VersionedMixin


class UserSession(Base, TimestampMixin, VersionedMixin):
    """
    Represents a user session recording actions and associated roles.
    """

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="sessions")
    session_roles: Mapped[list[SessionRole]] = relationship(
        "SessionRole",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "action", name="uq_user_session_user_action"),
        Index("ix_user_sessions_user_id_created_at", "user_id", "created_at"),
    )

    # Utility Methods

    def log_action(self, action: str, details: dict[str, Any]) -> None:
        """
        Log an action with details.

        Args:
            action (str): The action to log.
            details (Dict[str, Any]): Additional details about the action.
        """
        self.action = action
        self.details = details

    def assign_session_role(self, role: Role) -> None:
        """
        Assign a role to this session.

        Args:
            role (Role): The role to assign.
        """
        session_role = SessionRole(session=self, role=role)
        self.session_roles.append(session_role)

    def __repr__(self) -> str:
        return (
            f"<UserSession(id={self.id}, user_id={self.user_id}, action='{self.action}', "
            f"created_at={self.created_at})>"
        )
