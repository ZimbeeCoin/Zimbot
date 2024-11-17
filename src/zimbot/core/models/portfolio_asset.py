# src/zimbot/core/models/portfolio_asset.py

from __future__ import annotations  # Enable forward references for type hints

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .portfolio import Portfolio, TimestampMixin, VersionedMixin


class PortfolioAsset(Base, TimestampMixin, VersionedMixin):
    """
    Represents an asset within a user's portfolio.
    """

    __tablename__ = "portfolio_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[float] = mapped_column(
        Numeric(precision=18, scale=8), nullable=False
    )
    average_price: Mapped[float | None] = mapped_column(
        Numeric(precision=18, scale=8), nullable=True
    )
    current_price: Mapped[float | None] = mapped_column(
        Numeric(precision=18, scale=8), nullable=True
    )
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    portfolio: Mapped[Portfolio] = relationship("Portfolio", back_populates="assets")

    __table_args__ = (
        Index("ix_portfolio_assets_symbol_portfolio", "portfolio_id", "symbol"),
        Index("ix_portfolio_assets_updated_at", "updated_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<PortfolioAsset(id={self.id}, portfolio_id={self.portfolio_id}, "
            f"symbol='{self.symbol}', quantity={self.quantity}, "
            f"average_price={self.average_price}, current_price={self.current_price}, "
            f"disabled={self.disabled})>"
        )
