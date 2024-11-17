# tests/unit/finance/test_finance_client.py
from unittest.mock import AsyncMock

import pytest
from finance.client.finance_data_client import DataFetchError, FinanceClient
from finance.types.livecoinwatch_types import CoinData, LiveCoinWatchResponse


@pytest.mark.asyncio
async def test_get_real_time_price_success(monkeypatch):
    # Mock data
    mock_response = LiveCoinWatchResponse(
        data=[
            CoinData(
                id="bitcoin",
                symbol="BTC",
                name="Bitcoin",
                rate=50000.0,
                volume=1000000.0,
                cap=900000000000.0,
                totalSupply=21000000.0,
                circulatingSupply=18500000.0,
                maxSupply=21000000.0,
                delta=None,
            )
        ]
    )

    # Mock fetch_coin_data method
    async def mock_fetch_coin_data(
        currency: str, codes: List[str]
    ) -> LiveCoinWatchResponse:
        return mock_response

    monkeypatch.setattr(
        "finance.internal.livecoinwatch.LiveCoinWatchClient.fetch_coin_data",
        mock_fetch_coin_data,
    )

    # Instantiate FinanceClient with mocked LiveCoinWatchClient
    finance_client = FinanceClient()

    # Test
    response = await finance_client.get_real_time_price("BTC", "USD")
    assert response.symbol == "BTC"
    assert response.rate == 50000.0


@pytest.mark.asyncio
async def test_get_real_time_price_failure(monkeypatch):
    # Mock fetch_coin_data method to raise an error
    async def mock_fetch_coin_data(
        currency: str, codes: List[str]
    ) -> LiveCoinWatchResponse:
        raise DataFetchError("Failed to fetch data")

    monkeypatch.setattr(
        "finance.internal.livecoinwatch.LiveCoinWatchClient.fetch_coin_data",
        mock_fetch_coin_data,
    )

    # Instantiate FinanceClient with mocked LiveCoinWatchClient
    finance_client = FinanceClient()

    # Test
    with pytest.raises(DataFetchError) as exc_info:
        await finance_client.get_real_time_price("BTC", "USD")

    assert "Failed to fetch data" in str(exc_info.value)
