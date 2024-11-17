# src/finance/types/livecoinwatch_types.py
from typing import List, Optional

from pydantic import BaseModel, Field


class CoinDelta(BaseModel):
    """Represents change in price over various time periods."""

    day: Optional[float] = None
    week: Optional[float] = None
    month: Optional[float] = None
    quarter: Optional[float] = None
    year: Optional[float] = None


class CoinData(BaseModel):
    """Data model for individual coin data."""

    id: str
    symbol: str
    name: str
    rate: float
    volume: Optional[float] = None
    cap: Optional[float] = None
    totalSupply: Optional[float] = None
    circulatingSupply: Optional[float] = None
    maxSupply: Optional[float] = None
    delta: Optional[CoinDelta] = None


class LiveCoinWatchResponse(BaseModel):
    """Represents the response from the LiveCoinWatch API."""

    data: List[CoinData]
