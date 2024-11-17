"""
Core financial metrics and market data type definitions.

This module contains the fundamental data structures used for
financial calculations and market analysis.

Usage:
    from zimbot.finance.types.core_metrics import FinancialMetrics

    metrics = FinancialMetrics(
        timestamp=datetime.now(),
        value=100.0,
        change_24h=-2.5
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class FinancialMetrics:
    timestamp: datetime = field(
        metadata={
            "description": "Timestamp of the metric measurement",
            "example": "2024-01-01T12:00:00Z",
        }
    )
    value: Decimal = field(
        metadata={"description": "Current value/price", "example": "45000.50"}
    )
    change_24h: Optional[Decimal] = field(
        default=None,
        metadata={
            "description": "24-hour price change in percentage",
            "example": "-2.5",
        },
    )
    volume_24h: Optional[Decimal] = field(
        default=None,
        metadata={
            "description": "24-hour trading volume in base currency",
            "example": "1000000.00",
        },
    )


@dataclass
class MarketData:
    symbol: str = field(
        metadata={"description": "Trading pair symbol", "example": "BTC/USD"}
    )
    price: Decimal = field(
        metadata={
            "description": "Current market price in quote currency",
            "example": "45000.50",
        }
    )
    metrics: FinancialMetrics = field(
        default_factory=lambda: FinancialMetrics(
            timestamp=datetime.now(), value=Decimal("0.0")
        ),
        metadata={
            "description": "Associated financial metrics for this market data point"
        },
    )
