import pytest

from zimbot.finance import AnalysisConfig, FinanceClient


@pytest.fixture
async def finance_client():
    config = AnalysisConfig(
        time_period="1d",
        metrics=["roi", "volatility", "sharpe_ratio"],
        risk_threshold=0.05,
    )
    return FinanceClient(config)


async def test_market_analysis(finance_client):
    metrics, market_data = await finance_client.analyze_market("BTC")
    assert metrics is not None
    assert market_data is not None
    assert isinstance(metrics.total_value, float)
    assert "price" in market_data


async def test_real_time_price(finance_client):
    price_data = await finance_client.get_real_time_price("BTC")
    assert price_data is not None
    assert "rate" in price_data
    assert "volume" in price_data


# Usage example in your application:
async def example_usage():
    # Initialize the finance client
    client = FinanceClient()

    # Get market analysis
    metrics, market_data = await client.analyze_market("BTC")

    # Get real-time price
    price_data = await client.get_real_time_price("BTC")

    # Get technical analysis
    technical_data = await client.get_technical_analysis("BTC")

    return {
        "metrics": metrics,
        "market": market_data,
        "price": price_data,
        "technical": technical_data,
    }
