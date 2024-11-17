# src/finance/client/client.py
from typing import Dict, List, Optional, Tuple

from core.utils.logger import get_logger
from finance.internal.analysis import AnalysisEngine, AnalysisError
from finance.internal.coinapi import CoinAPIClient, CoinAPIDataFetchError
from finance.internal.livecoinwatch import (
    LiveCoinWatchClient,
    LiveCoinWatchDataFetchError,
)
from finance.types.livecoinwatch_types import CoinData, LiveCoinWatchResponse
from finance.types.types import AnalysisConfig, FinancialMetrics, MarketData

logger = get_logger(__name__)


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""

    pass


class FinanceClient:
    """Main interface for financial analysis and market data."""

    def __init__(
        self,
        lcw_client: Optional[LiveCoinWatchClient] = None,
        coin_api_client: Optional[CoinAPIClient] = None,
        analysis_engine: Optional[AnalysisEngine] = None,
        config: Optional[AnalysisConfig] = None,
    ):
        self.config = config or AnalysisConfig()
        self._lcw_client = lcw_client or LiveCoinWatchClient()
        self._coin_api_client = coin_api_client or CoinAPIClient()
        self._analysis_engine = analysis_engine or AnalysisEngine()

    async def analyze_market(
        self, symbol: str, currency: str = "USD"
    ) -> Tuple[FinancialMetrics, MarketData]:
        """
        Perform comprehensive market analysis.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC")
            currency: Quote currency (default: USD)

        Returns:
            Tuple of FinancialMetrics and MarketData

        Raises:
            AnalysisError: If an error occurs during analysis
            DataFetchError: If data fetching fails
        """
        try:
            metrics, market_data = await self._analysis_engine.analyze(
                symbol=symbol,
                currency=currency,
                lcw_client=self._lcw_client,
                coin_api_client=self._coin_api_client,
            )
            return metrics, market_data
        except AnalysisError as e:
            logger.error(f"Analysis error for symbol {symbol}: {e}")
            raise
        except (LiveCoinWatchDataFetchError, CoinAPIDataFetchError) as e:
            logger.error(
                f"Data fetch error during market analysis for symbol {symbol}: {e}"
            )
            raise DataFetchError(
                f"Failed to fetch required data for market analysis: {e}"
            )

    async def get_real_time_price(
        self, symbol: str, currency: str = "USD"
    ) -> MarketData:
        """
        Get real-time price data for a cryptocurrency symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC")
            currency: Quote currency (default: USD)

        Returns:
            MarketData object containing real-time price data.

        Raises:
            DataFetchError: If data cannot be fetched from LiveCoinWatch
        """
        try:
            response: LiveCoinWatchResponse = await self._lcw_client.fetch_coin_data(
                currency=currency, codes=[symbol]
            )
            if not response.data:
                raise DataFetchError(f"No data returned for symbol {symbol}")
            return response.data[
                0
            ]  # Assuming single symbol request returns one CoinData
        except LiveCoinWatchDataFetchError as e:
            logger.error(f"Error fetching real-time price for {symbol}: {e}")
            raise DataFetchError(f"Failed to fetch real-time price for {symbol}: {e}")

    async def get_technical_analysis(self, symbol: str, currency: str = "USD") -> Dict:
        """
        Get technical analysis data for a cryptocurrency symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC")
            currency: Quote currency (default: USD)

        Returns:
            Dictionary with technical analysis data.

        Raises:
            AnalysisError: If technical analysis cannot be completed.
            DataFetchError: If data fetching fails.
        """
        try:
            return await self._analysis_engine.get_technical_indicators(
                symbol=symbol,
                currency=currency,
                coin_api_client=self._coin_api_client,
            )
        except AnalysisError as e:
            logger.error(f"Error in technical analysis for {symbol}: {e}")
            raise
        except CoinAPIDataFetchError as e:
            logger.error(
                f"Error fetching data for technical analysis for {symbol}: {e}"
            )
            raise DataFetchError(f"Failed to fetch data for technical analysis: {e}")

    async def close_sessions(self):
        """Close any open sessions for clients."""
        await self._lcw_client.close_session()
        await self._coin_api_client.close_session()
