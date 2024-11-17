# src/zimbot/core/integrations/openai/dependencies.py

from typing import Any, Dict, Generator

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError

from .service_manager import OpenAIServiceManager


async def get_openai_clients() -> Generator[OpenAIServiceManager, None, None]:
    """
    Initialize and provide OpenAIServiceManager.

    Yields:
        OpenAIServiceManager: Initialized OpenAI service manager.
    """
    manager = OpenAIServiceManager(settings.openai.service_accounts)
    try:
        await manager.start()
        yield manager
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI clients: {e}")
        raise IntegrationError(f"Failed to initialize OpenAI clients: {e}") from e
    finally:
        await manager.shutdown()
