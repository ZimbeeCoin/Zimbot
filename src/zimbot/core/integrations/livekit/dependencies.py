# src/zimbot/core/integrations/livekit/dependencies.py

from typing import Generator

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError
from zimbot.core.integrations.livekit.client import LiveKitManager


async def get_livekit_integration() -> Generator[LiveKitManager, None, None]:
    """
    Initialize and provide LiveKitManager.

    Yields:
        LiveKitManager: Initialized LiveKit manager.
    """
    manager = LiveKitManager(
        api_key=settings.livekit.api_key.get_secret_value(),
        api_secret=settings.livekit.api_secret.get_secret_value(),
        host=settings.livekit.host,
    )
    try:
        await manager.start()
        yield manager
    except Exception as e:
        logger.error(f"Failed to initialize LiveKit integration: {e}")
        raise IntegrationError(f"Failed to initialize LiveKit integration: {e}") from e
    finally:
        await manager.shutdown()
