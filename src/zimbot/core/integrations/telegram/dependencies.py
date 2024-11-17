# src/zimbot/core/integrations/telegram/dependencies.py

from typing import Generator

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError
from zimbot.core.integrations.telegram.bot import TelegramBotManager


async def get_telegram_bot() -> Generator[TelegramBotManager, None, None]:
    """
    Initialize and provide the TelegramBotManager.

    Yields:
        TelegramBotManager: Initialized Telegram bot manager.
    """
    try:
        bot_manager = TelegramBotManager(settings.telegram_bot.token.get_secret_value())
        await bot_manager.start()
        yield bot_manager
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        raise IntegrationError(f"Failed to initialize Telegram bot: {e}") from e
    finally:
        await bot_manager.stop()
