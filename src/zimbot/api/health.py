# src/zimbot/api/health.py

from typing import Dict

from fastapi import APIRouter, Depends

from zimbot.core.integrations.crypto_client import CryptoClient
from zimbot.core.integrations.dependencies import get_crypto_clients
from zimbot.core.integrations.finance.client import FinanceClient
from zimbot.core.integrations.finance.dependencies import get_financial_client
from zimbot.core.integrations.livekit.client import (
    LiveKitManager,
    get_livekit_integration,
)
from zimbot.core.integrations.openai.dependencies import get_openai_clients
from zimbot.core.integrations.openai.service_manager import OpenAIServiceManager
from zimbot.core.integrations.telegram.bot import TelegramBotManager, get_telegram_bot

router = APIRouter()


@router.get("/", tags=["Health Check"])
async def health_check(
    openai_manager: OpenAIServiceManager = Depends(get_openai_clients),
    finance_client: FinanceClient = Depends(get_financial_client),
    crypto_clients: Dict[str, CryptoClient] = Depends(get_crypto_clients),
    telegram_bot: TelegramBotManager = Depends(get_telegram_bot),
    livekit: LiveKitManager = Depends(get_livekit_integration),
):
    """
    Comprehensive health check endpoint that verifies the status of external services.
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

    # Check if all services are healthy
    overall_status = all(
        service_status for service_status in health_status["services"].values()
    )
    health_status["status"] = "ok" if overall_status else "unhealthy"

    # Log health check result
    logger.info({"event": "health_check", "status": health_status})

    return health_status
