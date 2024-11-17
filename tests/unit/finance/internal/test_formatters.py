# tests/finance/internal/test_formatters.py

import pytest
from finance.internal.formatters import (
    AnalysisFormatType,
    FinancialFormatter,
    FormattingError,
    MarketAnalysis,
    PortfolioData,
    ResearchFormatter,
    TechnicalIndicators,
)
from pydantic import ValidationError


def test_format_market_analysis_detailed():
    # Arrange
    technical_indicators = TechnicalIndicators(
        momentum={"SMA": 50, "EMA": 200},
        trend={"direction": "uptrend"},
        volatility={"ATR": 1.5},
        volume={"OBV": 10000},
    )
    market_analysis = MarketAnalysis(
        technical_indicators=technical_indicators,
        trading_signals=[
            {
                "symbol": "AAPL",
                "type": "buy",
                "direction": "up",
                "strength": "strong",
                "confidence": 0.9,
                "triggers": ["price_crosses_SMA"],
                "source": "technical_indicators",
                "method": "SMA crossover",
                "timeframe": "daily",
            }
        ],
        support_levels=[150.0, 145.0],
        resistance_levels=[155.0, 160.0],
    )

    # Act
    formatted = FinancialFormatter.format_market_analysis(
        analysis=market_analysis, format_type=AnalysisFormatType.DETAILED
    )

    # Assert
    assert "timestamp" in formatted
    assert "technical_indicators" in formatted
    assert formatted["technical_indicators"] == technical_indicators.dict()
    assert "sentiment_analysis" in formatted
    assert formatted["sentiment_analysis"] == {}
    assert "correlation_matrix" in formatted
    assert formatted["correlation_matrix"] == {}
    assert "confidence_metrics" in formatted
    assert formatted["confidence_metrics"] == {}


def test_format_market_analysis_technical():
    # Arrange
    market_analysis = MarketAnalysis(
        momentum_indicators={"RSI": 70},
        trend_indicators={"direction": "uptrend"},
        volatility_indicators={"ATR": 1.5},
        volume_indicators={"OBV": 10000},
        trading_signals=[
            {
                "symbol": "GOOGL",
                "type": "sell",
                "direction": "down",
                "strength": "moderate",
                "confidence": 0.7,
                "triggers": ["price_falls_below_EMA"],
                "source": "trend_indicators",
                "method": "EMA crossover",
                "timeframe": "weekly",
            }
        ],
        support_levels=[2500.0],
        resistance_levels=[2700.0, 2750.0],
    )

    # Act
    formatted = FinancialFormatter.format_market_analysis(
        analysis=market_analysis, format_type=AnalysisFormatType.TECHNICAL
    )

    # Assert
    assert "timestamp" in formatted
    assert "indicators" in formatted
    assert formatted["indicators"]["momentum"] == {"RSI": 70}
    assert formatted["indicators"]["trend"] == {"direction": "uptrend"}
    assert formatted["indicators"]["volatility"] == {"ATR": 1.5}
    assert formatted["indicators"]["volume"] == {"OBV": 10000}
    assert "signals" in formatted
    assert len(formatted["signals"]) == 1
    assert "levels" in formatted
    assert formatted["levels"]["support"] == [2500.0]
    assert formatted["levels"]["resistance"] == [2700.0, 2750.0]


def test_format_market_analysis_invalid_format_type():
    # Arrange
    market_analysis = MarketAnalysis()

    # Act & Assert
    with pytest.raises(FormattingError):
        FinancialFormatter.format_market_analysis(
            analysis=market_analysis,
            format_type="invalid_type",  # Invalid format type
        )


def test_format_portfolio_analysis():
    # Arrange
    portfolio_data = PortfolioData(
        total_value=1000000,
        currency="USD",
        positions=[{"asset": "AAPL", "quantity": 50, "price": 150}],
        asset_allocation={"AAPL": 50.0, "GOOGL": 30.0, "TSLA": 20.0},
        sector_allocation={"Technology": 60.0, "Automotive": 40.0},
        region_allocation={"US": 70.0, "Europe": 30.0},
        concentration_risk={"AAPL": 50.0},
        var_analysis={"VaR_95": 50000.0},
        stress_tests=[{"scenario": "market_crash", "impact": -100000}],
        rebalancing_needs=[{"asset": "TSLA", "action": "buy", "quantity": 10}],
        risk_recommendations=[
            "Diversify asset holdings",
            "Implement stop-loss orders",
        ],
        investment_opportunities=[
            {"asset": "AMZN", "reason": "Strong growth prospects"}
        ],
    )
    risk_metrics = {"VaR": 50000.0, "Expected Shortfall": 75000.0}

    # Act
    formatted = FinancialFormatter.format_portfolio_analysis(
        portfolio=portfolio_data, risk_metrics=risk_metrics
    )

    # Assert
    assert "timestamp" in formatted
    assert "portfolio_summary" in formatted
    assert formatted["portfolio_summary"]["total_value"] == 1000000
    assert formatted["portfolio_summary"]["currency"] == "USD"
    assert "positions" in formatted["portfolio_summary"]
    assert formatted["risk_analysis"]["metrics"] == risk_metrics
    assert "recommendations" in formatted
    assert len(formatted["recommendations"]["risk_management"]) == 2


def test_format_sector_analysis():
    # Arrange
    sector_data = {
        "sector": "Healthcare",
        "summary": "Overview of the healthcare sector.",
        "trends": ["Telemedicine", "Personalized Medicine"],
        "market_size": "$3 trillion",
        "growth_rate": "8% annually",
        "competition": {"major_players": ["Pfizer", "Johnson & Johnson"]},
        "regulations": {"FDA": "Stringent approval processes"},
        "technology": {"AI in diagnostics": "Growing adoption"},
        "dynamics": {"demand": "Increasing with aging population"},
        "opportunities": ["Expansion in emerging markets"],
        "risks": ["Regulatory changes"],
        "recommendations": ["Invest in telemedicine startups"],
        "sources": ["Bloomberg", "Reuters"],
        "notes": ["High potential for AI integration"],
    }
    analysis_depth = "comprehensive"

    # Act
    formatted = ResearchFormatter.format_sector_analysis(
        sector_data=sector_data, analysis_depth=analysis_depth
    )

    # Assert
    assert "timestamp" in formatted
    assert formatted["sector"] == "Healthcare"
    assert formatted["overview"]["summary"] == "Overview of the healthcare sector."
    assert formatted["analysis"]["competitive_landscape"] == {
        "major_players": ["Pfizer", "Johnson & Johnson"]
    }
    assert formatted["metadata"]["analysis_depth"] == "comprehensive"
    assert formatted["metadata"]["data_sources"] == ["Bloomberg", "Reuters"]
    assert formatted["metadata"]["analyst_notes"] == [
        "High potential for AI integration"
    ]


def test_format_sector_analysis_invalid_depth():
    # Arrange
    sector_data = {}

    # Act & Assert
    with pytest.raises(FormattingError):
        ResearchFormatter.format_sector_analysis(
            sector_data=sector_data, analysis_depth="invalid_depth"
        )
