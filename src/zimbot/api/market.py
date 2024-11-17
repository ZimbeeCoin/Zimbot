# src/zimbot/api/market.py
"""
Market Data API

This module provides endpoints for retrieving cryptocurrency market data.
It includes functionality to fetch data for specified cryptocurrencies and ensures
secure access using OAuth2 token authentication.

Dependencies:
    - FastAPI: Provides API routing and exception handling.
    - FinanceClient: A client for interacting with external market data sources.
    - OAuth2PasswordBearer: Ensures that requests are authenticated with a valid token.

Endpoints:
    - POST /market/data: Fetches market data for specified cryptocurrencies.
"""

from typing import List

from core.utils.logger import get_logger
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from finance.client.finance_data_client import DataFetchError, FinanceClient
from finance.dependencies import get_finance_client
from finance.types.livecoinwatch_types import LiveCoinWatchResponse
from jose import JWTError, jwt
from pydantic import ValidationError

from zimbot.core.config.config import settings

router = APIRouter(prefix="/market", tags=["Market Data"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
logger = get_logger(__name__)

# Mock user database for demonstration (replace with actual database integration)
fake_users_db = {
    "alice": {"username": "alice"},
    "bob": {"username": "bob"},
}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on the provided OAuth2 token.

    Args:
        token (str): The JWT token for authentication, retrieved from the OAuth2 scheme.

    Returns:
        dict: A dictionary representing the user if authentication is successful.

    Raises:
        HTTPException: If the token is invalid or user does not exist, raises a 401 Unauthorized error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=["HS256"],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/data", response_model=LiveCoinWatchResponse)
async def market_data(
    currency: str,
    codes: List[str],
    finance_client: FinanceClient = Depends(get_finance_client),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch market data for specified cryptocurrencies.

    Args:
        currency (str): The currency to quote the coin prices (e.g., "USD").
        codes (List[str]): List of cryptocurrency symbols to fetch data for (e.g., ["BTC", "ETH"]).
        finance_client (FinanceClient): An instance of FinanceClient for interacting with market data sources.
        current_user (dict): The current authenticated user, provided by dependency injection.

    Returns:
        LiveCoinWatchResponse: A response object containing data for the requested cryptocurrencies.

    Raises:
        HTTPException: Raises a 500 error if data fetching fails or if an unexpected error occurs.
    """
    try:
        response = await finance_client._lcw_client.fetch_coin_data(
            currency=currency, codes=codes
        )
        return response
    except DataFetchError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
