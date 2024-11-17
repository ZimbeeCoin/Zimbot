# src/zimbot/core/models/session_role.py

from __future__ import annotations  # Enable forward references for type hints

from typing import Optional

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .role import Role  # Import Role from role.py
from .user_session import TimestampMixin, UserSession


class SessionRole(Base, TimestampMixin):
    """
    Represents the association between a user session and a role.
    """

    __tablename__ = "session_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_sessions.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )

    session: Mapped[UserSession] = relationship(
        "UserSession", back_populates="session_roles"
    )
    role: Mapped[Role] = relationship("Role")

    __table_args__ = (
        UniqueConstraint("session_id", "role_id", name="uq_session_role"),
        Index("ix_session_roles_session_id_role_id", "session_id", "role_id"),
    )

    def __repr__(self) -> str:
        return f"<SessionRole(id={self.id}, session_id={self.session_id}, role_id={self.role_id})>"
