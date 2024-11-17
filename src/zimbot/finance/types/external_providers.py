"""
Type definitions for external financial data providers.

This module contains type definitions that match the response
structures of various external API providers.

Supported Providers:
- LiveCoinWatch
- CoinAPI
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class LiveCoinWatchResponse:
    code: str = field(
        metadata={
            "description": "Currency code (e.g., 'BTC')",
            "example": "BTC",
        }
    )
    rate: Decimal = field(
        metadata={
            "description": "Exchange rate against base currency",
            "example": "45000.50",
        }
    )
    meta: Optional[Dict[str, Any]] = field(
        default=None,
        metadata={
            "description": "Provider metadata including timestamp, source, etc.",
            "example": {
                "timestamp": "2024-01-01T12:00:00Z",
                "source": "livecoinwatch",
                "refresh_rate": "60s",
            },
        },
    )


@dataclass
class CoinData:
    symbol: str = field(metadata={"description": "Coin/token symbol", "example": "BTC"})
    price: Decimal = field(
        metadata={
            "description": "Current price in base currency",
            "example": "45000.50",
        }
    )
    volume: Decimal = field(
        metadata={
            "description": "Trading volume in base currency",
            "example": "1000000.00",
        }
    )
