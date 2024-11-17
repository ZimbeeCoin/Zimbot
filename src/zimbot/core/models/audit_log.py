# src/zimbot/core/models/audit_log.py

from __future__ import annotations  # Enable forward references for type hints

from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from .base import Base  # Import Base from base.py
from .user import TimestampMixin, User  # Import related models and mixins


class AuditLog(Base, TimestampMixin):
    """
    Represents an audit log entry recording user actions for security, tracking, and accountability.
    """

    __tablename__ = "audit_logs"

    # Primary ID for the log entry
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to reference the user who performed the action
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # A brief description of the action
    action: Mapped[str] = mapped_column(String(255), nullable=False)

    # Additional structured data about the action
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationship to the User model
    user: Mapped[User] = relationship("User", back_populates="audit_logs")

    # Indexes for optimized querying by user and action time
    __table_args__ = (
        Index("ix_audit_logs_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, user_id={self.user_id}, "
            f"action='{self.action}', created_at={self.created_at})>"
        )

    @classmethod
    def log_action(
        cls,
        session: Session,
        user_id: int | None,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Creates and commits an audit log entry.

        Args:
            session (Session): The SQLAlchemy session to use for committing the entry.
            user_id (Optional[int]): The ID of the user performing the action. Can be None.
            action (str): A brief description of the action.
            details (Optional[Dict[str, Any]]): Additional details about the action.

        Raises:
            ValueError: If the action is not provided.
            RuntimeError: If committing the audit log entry fails.
        """
        if not action:
            raise ValueError("Action description is required to log an audit event.")

        audit_entry = cls(
            user_id=user_id,
            action=action,
            details=details or {},
        )

        session.add(audit_entry)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to log audit action: {e}") from e
