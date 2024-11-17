"""
Type definitions for the finance package.

Provides comprehensive type definitions for financial data structures,
organized into two main categories:
    - core_metrics: Fundamental financial and market data types
    - external_providers: Type definitions for external API providers

Usage:
    from zimbot.finance.types import FinancialMetrics, LiveCoinWatchResponse

    metrics = FinancialMetrics(timestamp=datetime.now(), value=100.0)
    response = LiveCoinWatchResponse(code="BTC", rate=50000.0)
"""

from .core_metrics import FinancialMetrics, MarketData
from .external_providers import CoinData, LiveCoinWatchResponse

# Public API surface for finance types
__all__ = [
    # Core financial metric types
    "FinancialMetrics",
    "MarketData",
    # External provider response types
    "LiveCoinWatchResponse",
    "CoinData",
]
