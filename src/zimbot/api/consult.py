"""
Consultation Services API

This module provides endpoints for consultation services related to financial
market analysis. It includes an endpoint to perform a comprehensive market analysis
using provided market data and a specified analysis type.

Dependencies:
    - FastAPI: Provides API routing and exception handling.
    - FinanceClient: A client for performing financial data analysis, injected as a dependency.

Endpoints:
    - POST /consult/analyze: Perform a market analysis with specified data and analysis type.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from finance.client.finance_data_client import DataFetchError, FinanceClient

from zimbot.finance.dependencies import get_finance_client

router = APIRouter(prefix="/consult", tags=["Consultation Services"])


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_market(
    market_data: Dict[str, Any],
    analysis_type: str = "comprehensive",
    finance_client: FinanceClient = Depends(get_finance_client),
) -> Dict[str, Any]:
    """
    Perform a market analysis based on provided market data and analysis type.

    Args:
        market_data (Dict[str, Any]): A dictionary containing relevant market data.
                                      Expected to include keys such as 'symbol', 'price', etc.
        analysis_type (str): The type of analysis to perform. Options include "comprehensive".
                             Defaults to "comprehensive".
        finance_client (FinanceClient): Instance of FinanceClient, provided via dependency injection.

    Returns:
        Dict[str, Any]: A dictionary containing the analysis results.

    Raises:
        HTTPException (500): If data fetching fails due to a DataFetchError.
        HTTPException (500): If an unexpected error occurs during analysis.
    """
    try:
        response = await finance_client.analyze_market_data(
            market_data=market_data, analysis_type=analysis_type
        )
        return response
    except DataFetchError as e:
        raise HTTPException(status_code=500, detail=f"Data fetch error: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during market analysis.",
        )
