# src/finance/internal/formatters.py

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AnalysisFormatType(str, Enum):
    """Types of analysis formats available"""

    BRIEF = "brief"
    DETAILED = "detailed"
    TECHNICAL = "technical"


class FormattingError(ValueError):
    """Custom error for formatting issues."""

    pass


def _get_timestamp() -> str:
    """Helper function to get the current UTC timestamp."""
    return datetime.utcnow().isoformat()


class MarketMetrics(BaseModel):
    """Market analysis metrics"""

    technical_indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    sentiment_analysis: Optional[Dict[str, Any]] = Field(default_factory=dict)
    correlation_matrix: Optional[Dict[str, Any]] = Field(default_factory=dict)
    confidence_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators"""

    momentum: Optional[Dict[str, Any]] = Field(default_factory=dict)
    trend: Optional[Dict[str, Any]] = Field(default_factory=dict)
    volatility: Optional[Dict[str, Any]] = Field(default_factory=dict)
    volume: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MarketAnalysis(BaseModel):
    """Market analysis data structure"""

    technical_indicators: Optional[TechnicalIndicators]
    momentum_indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    trend_indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    volatility_indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    volume_indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    trading_signals: List[Dict[str, Any]] = Field(default_factory=list)
    support_levels: List[float] = Field(default_factory=list)
    resistance_levels: List[float] = Field(default_factory=list)


class PortfolioData(BaseModel):
    """Portfolio data structure"""

    total_value: float
    currency: str = "USD"
    positions: List[Dict[str, Any]] = Field(default_factory=list)
    asset_allocation: Dict[str, float] = Field(default_factory=dict)
    sector_allocation: Dict[str, float] = Field(default_factory=dict)
    region_allocation: Dict[str, float] = Field(default_factory=dict)
    concentration_risk: Dict[str, Any] = Field(default_factory=dict)
    var_analysis: Dict[str, Any] = Field(default_factory=dict)
    stress_tests: List[Dict[str, Any]] = Field(default_factory=list)
    rebalancing_needs: List[Dict[str, Any]] = Field(default_factory=list)
    risk_recommendations: List[str] = Field(default_factory=list)
    investment_opportunities: List[Dict[str, Any]] = Field(default_factory=list)


class FinancialFormatter:
    """Formats financial analysis responses with validation"""

    @staticmethod
    def format_market_analysis(
        analysis: MarketAnalysis,
        format_type: AnalysisFormatType = AnalysisFormatType.DETAILED,
    ) -> Dict[str, Any]:
        """
        Formats market analysis response with validation and logging.

        Args:
            analysis (MarketAnalysis): Validated market analysis data
            format_type (AnalysisFormatType): Level of detail for the analysis output

        Returns:
            Dict[str, Any]: Structured market analysis with sections based on format_type
        """
        logger.info(f"Formatting market analysis with type: {format_type}")

        formatted = {
            "timestamp": _get_timestamp(),
            "market_conditions": {},
            "opportunities": [],
            "risks": [],
            "recommendations": [],
        }

        try:
            if format_type == AnalysisFormatType.DETAILED:
                logger.debug("Adding detailed metrics to market analysis")
                formatted.update(
                    {
                        "technical_indicators": (
                            analysis.technical_indicators.dict(exclude_none=True)
                            if analysis.technical_indicators
                            else {}
                        ),
                        "sentiment_analysis": analysis.sentiment_analysis or {},
                        "correlation_matrix": analysis.correlation_matrix or {},
                        "confidence_metrics": analysis.confidence_metrics or {},
                    }
                )

            elif format_type == AnalysisFormatType.TECHNICAL:
                logger.debug("Adding technical indicators to market analysis")
                formatted.update(
                    {
                        "indicators": {
                            "momentum": analysis.momentum_indicators,
                            "trend": analysis.trend_indicators,
                            "volatility": analysis.volatility_indicators,
                            "volume": analysis.volume_indicators,
                        },
                        "signals": analysis.trading_signals,
                        "levels": {
                            "support": analysis.support_levels,
                            "resistance": analysis.resistance_levels,
                        },
                    }
                )

            logger.info("Successfully formatted market analysis")
            return formatted

        except Exception as e:
            logger.error(f"Error formatting market analysis: {str(e)}")
            raise FormattingError(f"Failed to format market analysis: {str(e)}") from e

    @staticmethod
    def format_portfolio_analysis(
        portfolio: PortfolioData, risk_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Formats portfolio analysis with risk metrics and validation.

        Args:
            portfolio (PortfolioData): Validated portfolio data
            risk_metrics (Dict[str, float]): Dictionary of risk metrics and their values

        Returns:
            Dict[str, Any]: Structured portfolio analysis including:
                - portfolio_summary: Overall portfolio state
                - risk_analysis: Risk metrics and analysis
                - recommendations: Actionable recommendations
        """
        logger.info("Formatting portfolio analysis")

        try:
            formatted = {
                "timestamp": _get_timestamp(),
                "portfolio_summary": {
                    "total_value": portfolio.total_value,
                    "currency": portfolio.currency,
                    "positions": portfolio.positions,
                    "allocation": {
                        "by_asset": portfolio.asset_allocation,
                        "by_sector": portfolio.sector_allocation,
                        "by_region": portfolio.region_allocation,
                    },
                },
                "risk_analysis": {
                    "metrics": risk_metrics,
                    "concentration_risk": portfolio.concentration_risk,
                    "var_analysis": portfolio.var_analysis,
                    "stress_tests": portfolio.stress_tests,
                },
                "recommendations": {
                    "rebalancing": portfolio.rebalancing_needs,
                    "risk_management": portfolio.risk_recommendations,
                    "opportunities": portfolio.investment_opportunities,
                },
            }

            logger.info("Successfully formatted portfolio analysis")
            return formatted

        except Exception as e:
            logger.error(f"Error formatting portfolio analysis: {str(e)}")
            raise FormattingError(
                f"Failed to format portfolio analysis: {str(e)}"
            ) from e


class ResearchFormatter:
    """Formats research reports with validation"""

    @staticmethod
    def format_sector_analysis(
        sector_data: Dict[str, Any], analysis_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Formats sector analysis reports with validation and logging.

        Args:
            sector_data (Dict[str, Any]): Raw sector analysis data
            analysis_depth (str): Depth of analysis ('comprehensive', 'brief')

        Returns:
            Dict[str, Any]: Structured sector analysis with metadata
        """
        logger.info(f"Formatting sector analysis with depth: {analysis_depth}")

        try:
            formatted = {
                "timestamp": _get_timestamp(),
                "sector": sector_data.get("sector"),
                "overview": {
                    "summary": sector_data.get("summary"),
                    "key_trends": sector_data.get("trends", []),
                    "market_size": sector_data.get("market_size"),
                    "growth_rate": sector_data.get("growth_rate"),
                },
                "analysis": {
                    "competitive_landscape": sector_data.get("competition", {}),
                    "regulatory_environment": sector_data.get("regulations", {}),
                    "technological_factors": sector_data.get("technology", {}),
                    "market_dynamics": sector_data.get("dynamics", {}),
                },
                "opportunities": sector_data.get("opportunities", []),
                "risks": sector_data.get("risks", []),
                "recommendations": sector_data.get("recommendations", []),
                "metadata": {
                    "analysis_depth": analysis_depth,
                    "data_sources": sector_data.get("sources", []),
                    "analyst_notes": sector_data.get("notes", []),
                },
            }

            logger.info("Successfully formatted sector analysis")
            return formatted

        except Exception as e:
            logger.error(f"Error formatting sector analysis: {str(e)}")
            raise FormattingError(f"Failed to format sector analysis: {str(e)}") from e
