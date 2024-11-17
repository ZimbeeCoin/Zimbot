# src/zimbot/core/integrations/client/crypto_client.py

import asyncio
from typing import Any, Dict

import aiohttp

from zimbot.core.integrations.exceptions.exceptions import IntegrationError


class CryptoClient:
    def __init__(self, api_key: str, base_url: str, **kwargs: Any):
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self):
        """Initialize any necessary connections or sessions."""
        try:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            await asyncio.sleep(0.1)  # Simulate connection delay
        except Exception as e:
            raise IntegrationError(f"Failed to connect CryptoClient: {e}") from e

    def is_healthy(self) -> bool:
        """Check if the client is healthy."""
        return self.session is not None and not self.session.closed

    async def close(self):
        """Close any open connections or sessions."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_coin_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch the current price of a cryptocurrency."""
        if not self.session:
            raise IntegrationError("Session not initialized.")
        url = f"{self.base_url}/price?symbol={symbol}"
        async with self.session.get(url) as response:
            if response.status != 200:
                text = await response.text()
                raise IntegrationError(
                    f"Failed to fetch price for {symbol}: {response.status} - {text}"
                )
            return await response.json()

    async def get_exchange_rate(self, symbol: str, currency: str) -> Dict[str, Any]:
        """Fetch the exchange rate of a cryptocurrency to a specified currency."""
        if not self.session:
            raise IntegrationError("Session not initialized.")
        url = f"{self.base_url}/exchange-rate?symbol={symbol}&currency={currency}"
        async with self.session.get(url) as response:
            if response.status != 200:
                text = await response.text()
                raise IntegrationError(
                    f"Failed to fetch exchange rate for {symbol} to {currency}: {response.status} - {text}"
                )
            return await response.json()
