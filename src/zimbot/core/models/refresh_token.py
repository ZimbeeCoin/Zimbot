# src/zimbot/core/models/refresh_token.py

from __future__ import annotations  # Enable forward references for type hints

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import TimestampMixin, User, VersionedMixin
from .utils import default_expiration  # Import default_expiration from utils.py


class RefreshToken(Base, TimestampMixin, VersionedMixin):
    """
    Represents a refresh token for user authentication.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=default_expiration
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    issuance_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (Index("ix_refresh_tokens_expires_at", "expires_at"),)

    # Utility Methods

    @property
    def is_expired(self) -> bool:
        """
        Check if the refresh token is expired.

        Returns:
            bool: True if the token is expired, False otherwise.
        """
        return datetime.utcnow() >= self.expires_at

    def increment_issuance(self) -> None:
        """
        Increment the issuance count for rate-limiting.
        """
        self.issuance_count += 1

    def __repr__(self) -> str:
        return (
            f"<RefreshToken(id={self.id}, user_id={self.user_id}, token='{self.token}', "
            f"expires_at={self.expires_at}, revoked={self.revoked}, issuance_count={self.issuance_count})>"
        )
