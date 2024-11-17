# src/zimbot/core/models/portfolio.py

from __future__ import annotations  # Enable forward references for type hints

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .portfolio_asset import PortfolioAsset  # Ensure this model is defined similarly
from .user import TimestampMixin, User, VersionedMixin


class Portfolio(Base, TimestampMixin, VersionedMixin):
    """
    Represents a user's portfolio containing various assets.
    """

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_synced: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="portfolios")
    assets: Mapped[list[PortfolioAsset]] = relationship(
        "PortfolioAsset",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_portfolio_user_name"),
        Index("ix_portfolios_user_id_name", "user_id", "name"),
    )

    # Utility Method

    def get_active_assets(self) -> list[PortfolioAsset]:
        """
        Retrieve all active assets in the portfolio.

        Returns:
            List[PortfolioAsset]: A list of active PortfolioAsset instances.
        """
        return [asset for asset in self.assets if not asset.disabled]

    def __repr__(self) -> str:
        return (
            f"<Portfolio(id={self.id}, user_id={self.user_id}, name='{self.name}', "
            f"created_at={self.created_at}, updated_at={self.updated_at}, disabled={self.disabled})>"
        )
