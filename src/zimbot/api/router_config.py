# src/zimbot/api/router_config.py

from typing import Callable, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from zimbot.core.config.settings import settings
from zimbot.core.integrations.dependencies import (
    get_crypto_clients,
    get_financial_client,
    get_openai_clients,
)
from zimbot.core.integrations.exceptions.exceptions import (
    AuthenticationError,
    DataFetchError,
    IntegrationError,
    RateLimitError,
    ServiceUnavailableError,
    WebhookError,
)
from zimbot.core.integrations.livekit.dependencies import get_livekit_integration
from zimbot.core.integrations.telegram.dependencies import get_telegram_bot


# Define a generic rate limit dependency
def rate_limit_dependency(rate_limit: str) -> Callable:
    """
    Create a rate limiting dependency.

    Args:
        rate_limit (str): Rate limit string (e.g., "30/minute").

    Returns:
        Callable: Dependency callable for rate limiting.
    """
    limiter = (
        settings.rate_limit.limiter
    )  # Assuming a Limiter instance is defined in settings
    return limiter.limit(rate_limit)


def create_rate_limited_router(
    prefix: str,
    tags: List[str],
    rate_limit: str,
    dependencies: Optional[List[Any]] = None,
) -> APIRouter:
    """
    Create a router with rate limiting and default dependencies.

    Args:
        prefix (str): API prefix for the router.
        tags (List[str]): Tags for the router.
        rate_limit (str): Rate limit string (e.g., "30/minute").
        dependencies (Optional[List[Any]]): Additional dependencies.

    Returns:
        APIRouter: Configured APIRouter instance.
    """
    if dependencies is None:
        dependencies = []

    router = APIRouter(prefix=prefix, tags=tags)

    # Add rate limiting dependency
    router.dependencies.append(Depends(rate_limit_dependency(rate_limit)))

    # Add any additional dependencies
    for dep in dependencies:
        router.dependencies.append(Depends(dep))

    return router


# Example Router: Market Data

router_market = create_rate_limited_router(
    prefix="/market",
    tags=["Market Data"],
    rate_limit=settings.rate_limit.market_rate_limit,  # e.g., "30/minute"
    dependencies=[Depends(settings.dependencies.verify_api_key)],
)


@router_market.get("/price/{symbol}", summary="Get current price of a cryptocurrency")
async def get_price(symbol: str, crypto_clients=Depends(get_crypto_clients)):
    """
    Retrieve the current price of a specified cryptocurrency symbol.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., BTC, ETH).
        crypto_clients: Initialized crypto clients from dependencies.

    Returns:
        Dict[str, Any]: Cryptocurrency price data.
    """
    try:
        client = crypto_clients.get("livecoinwatch")
        if not client:
            raise IntegrationError("LiveCoinWatch client not available.")
        price_data = await client.get_coin_price(symbol)
        return price_data
    except IntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# Similar routers can be created for other API sections like consult,
# assistants, bots, etc.

# Example Router: Health Check

router_health = APIRouter(
    prefix="/health",
    tags=["Health Check"],
    dependencies=[Depends(settings.dependencies.verify_api_key)],
)


@router_health.get("/", summary="Comprehensive health check")
async def health_check(
    openai_manager: OpenAIServiceManager = Depends(get_openai_clients),
    finance_client: FinanceClient = Depends(get_financial_client),
    crypto_clients: Dict[str, CryptoClient] = Depends(get_crypto_clients),
    telegram_bot: TelegramBotManager = Depends(get_telegram_bot),
    livekit: LiveKitManager = Depends(get_livekit_integration),
):
    """
    Perform a comprehensive health check of all external services.

    Args:
        openai_manager: OpenAI service manager instance.
        finance_client: Financial data client instance.
        crypto_clients: Dictionary of crypto client instances.
        telegram_bot: Telegram bot manager instance.
        livekit: LiveKit integration instance.

    Returns:
        Dict[str, Any]: Health status of services.
    """
    health_status = {
        "status": "ok",
        "services": {
            "OpenAIServiceManager": openai_manager.is_healthy(),
            "FinanceClient": finance_client.is_healthy(),
            "CryptoClients": {
                name: client.is_healthy() for name, client in crypto_clients.items()
            },
            "TelegramBot": telegram_bot.is_running(),
            "LiveKit": livekit.is_healthy(),
            # Add other services as needed
        },
    }

    # Determine overall status
    overall_status = all(
        service_status for service_status in health_status["services"].values()
    )
    health_status["status"] = "ok" if overall_status else "unhealthy"

    # Log health check result
    logger.info({"event": "health_check", "status": health_status})

    return health_status
