# tests/integration/test_market_endpoint.py
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from finance.client.finance_data_client import DataFetchError, FinanceClient
from finance.types.livecoinwatch_types import CoinData, LiveCoinWatchResponse

from zimbot.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_market_data_endpoint_success(monkeypatch):
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

    # Send request to the endpoint
    response = client.post(
        "/v1/market/data", json={"currency": "USD", "codes": ["BTC"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["symbol"] == "BTC"
    assert data["data"][0]["rate"] == 50000.0


@pytest.mark.asyncio
async def test_market_data_endpoint_failure(monkeypatch):
    # Mock fetch_coin_data method to raise an error
    async def mock_fetch_coin_data(
        currency: str, codes: List[str]
    ) -> LiveCoinWatchResponse:
        raise DataFetchError("Failed to fetch data")

    monkeypatch.setattr(
        "finance.internal.livecoinwatch.LiveCoinWatchClient.fetch_coin_data",
        mock_fetch_coin_data,
    )

    # Send request to the endpoint
    response = client.post(
        "/v1/market/data", json={"currency": "USD", "codes": ["BTC"]}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to fetch data"
    assert "trace_id" in response.json()
