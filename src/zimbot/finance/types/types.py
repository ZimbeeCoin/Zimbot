from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class MarketData:
    price: float
    volume_24h: float
    market_cap: float
    change_24h: float
    last_updated: datetime
    additional_data: Dict


@dataclass
class TechnicalIndicators:
    sma_20: float
    sma_50: float
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    trend: str
    signals: Dict[str, str]


@dataclass
class FinancialMetrics:
    timestamp: datetime
    total_value: float
    profit_loss: float
    roi: float
    volatility: float
    metrics: Dict[str, float]
    technical_indicators: Optional[TechnicalIndicators] = None


@dataclass
class AnalysisConfig:
    time_period: str = "1d"
    metrics: List[str] = None
    risk_threshold: float = 0.05
    include_metadata: bool = False
    api_timeout: int = 30
    cache_duration: int = 300  # 5 minutes

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = ["roi", "volatility", "sharpe_ratio"]
