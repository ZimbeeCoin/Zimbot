# src/zimbot/core/integrations/dependencies.py

from typing import Any, Dict, Generator, Optional

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError

from .crypto_client import CryptoClient
from .openai.dependencies import get_financial_client, get_openai_clients


async def get_crypto_clients() -> Generator[Dict[str, CryptoClient], None, None]:
    """
    Initialize and provide crypto clients.

    Yields:
        Dict[str, CryptoClient]: Dictionary of initialized crypto clients.
    """
    clients = {}
    try:
        # Initialize LiveCoinWatch client
        livecoinwatch = CryptoClient(
            api_key=settings.livecoinwatch.api_key.get_secret_value(),
            base_url=settings.livecoinwatch.base_url,
        )
        await livecoinwatch.connect()
        clients["livecoinwatch"] = livecoinwatch

        # Initialize CoinAPI client
        coinapi = CryptoClient(
            api_key=settings.coinapi.api_key.get_secret_value(),
            base_url=settings.coinapi.base_url,
        )
        await coinapi.connect()
        clients["coinapi"] = coinapi

        yield clients
    except Exception as e:
        # Close any clients that were successfully initialized before the error
        for client in clients.values():
            await client.close()
        logger.error(f"Failed to initialize crypto clients: {e}")
        raise IntegrationError(f"Failed to initialize crypto clients: {e}") from e
    finally:
        # Ensure all clients are closed after usage
        for client in clients.values():
            await client.close()
