# src/finance/internal/livecoinwatch.py
from typing import List

import aiohttp
from core.config.config import settings
from core.utils.logger import get_logger
from finance.types.livecoinwatch_types import CoinData, LiveCoinWatchResponse
from pydantic import ValidationError

logger = get_logger(__name__)


class LiveCoinWatchDataFetchError(Exception):
    """Custom exception for LiveCoinWatch data fetching errors."""

    pass


class LiveCoinWatchClient:
    def __init__(self):
        self.api_key = settings.livecoinwatch_api_key_primary.get_secret_value()
        self.base_url = settings.livecoinwatch_base_url
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Ensure that we reuse the aiohttp session."""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.openai_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def fetch_coin_data(
        self, currency: str, codes: List[str]
    ) -> LiveCoinWatchResponse:
        """Fetches market data for specified coins from LiveCoinWatch."""
        url = f"{self.base_url}/coins/single"
        payload = {
            "currency": currency,
            "codes": codes,
            "meta": True,  # Optionally include additional metadata if supported
        }

        session = await self._get_session()

        try:
            async with session.post(
                url, json=payload, headers=self.headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"LiveCoinWatch API call failed: {response.status} - {error_text}"
                    )
                    raise LiveCoinWatchDataFetchError(
                        f"API Error: {response.status} - {error_text}"
                    )

                data = await response.json()

                # Parse and validate response data
                livecoinwatch_response = LiveCoinWatchResponse(**data)
                return livecoinwatch_response
        except aiohttp.ClientError as e:
            logger.error(f"Network error while accessing LiveCoinWatch API: {e}")
            raise LiveCoinWatchDataFetchError(f"Network Error: {e}")
        except ValidationError as e:
            logger.error(f"Data validation error: {e}")
            raise LiveCoinWatchDataFetchError(f"Validation Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise LiveCoinWatchDataFetchError(f"Unexpected Error: {e}")

    async def close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
