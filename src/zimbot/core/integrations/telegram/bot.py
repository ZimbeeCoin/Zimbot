# src/zimbot/core/integrations/telegram/bot.py

import logging
from typing import Any, Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError

logger = logging.getLogger(__name__)


class TelegramBotManager:
    def __init__(self, token: str):
        """
        Initialize the TelegramBotManager.

        Args:
            token (str): Telegram Bot API token.
        """
        self.token = token
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self._running: bool = False

    async def start(self):
        """Initialize and start the bot."""
        try:
            self.bot = Bot(token=self.token)
            self.dp = Dispatcher(self.bot)

            # Register message handlers
            self.dp.register_message_handler(
                self.handle_start_command, commands=["start"]
            )
            self.dp.register_message_handler(
                self.handle_help_command, commands=["help"]
            )
            self.dp.register_message_handler(
                self.handle_price_command, commands=["price"]
            )
            self.dp.register_message_handler(
                self.handle_message, content_types=["text"]
            )

            self._running = True

            # Start polling in a separate thread to prevent blocking
            executor.start_polling(
                self.dp, skip_updates=True, on_shutdown=self.stop_polling
            )
            logger.info("TelegramBotManager started polling.")
        except Exception as e:
            raise IntegrationError(f"Failed to start Telegram bot: {e}") from e

    async def stop(self):
        """Stop the bot and cleanup resources."""
        if self.bot:
            await self.bot.close()
            logger.info("Telegram bot closed.")
        self._running = False

    def is_running(self) -> bool:
        """Check if bot is running."""
        return self._running

    # Message Handlers
    async def handle_start_command(self, message: types.Message):
        """Handle /start command."""
        await message.reply("Welcome to ZimBot! Use /help to see available commands.")

    async def handle_help_command(self, message: types.Message):
        """Handle /help command."""
        help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/price <symbol> - Get crypto price
"""
        await message.reply(help_text)

    async def handle_price_command(self, message: types.Message):
        """
        Handle /price command to fetch cryptocurrency price.

        Args:
            message (types.Message): Incoming message containing the command.
        """
        try:
            args = message.get_args()
            if not args:
                await message.reply(
                    "Please provide a cryptocurrency symbol. Usage: /price <symbol>"
                )
                return

            symbol = args.strip().upper()
            # Here you would integrate with your crypto clients to fetch the price
            # For demonstration, we'll mock the response
            price_data = {"symbol": symbol, "price_usd": 1234.56}
            await message.reply(
                f"The current price of {symbol} is ${price_data['price_usd']:.2f} USD."
            )
        except Exception as e:
            logger.error(f"Error handling /price command: {e}")
            await message.reply(
                "An error occurred while fetching the price. Please try again later."
            )

    async def handle_message(self, message: types.Message):
        """Handle regular text messages."""
        await message.reply(
            "I'm sorry, I didn't understand that command. Use /help to see available commands."
        )

    def stop_polling(self):
        """Stop polling gracefully."""
        if self.dp:
            self.dp.stop_polling()
            logger.info("Stopped polling Telegram bot.")


# Dependency for FastAPI
async def get_telegram_bot() -> TelegramBotManager:
    """Get or create Telegram bot instance."""
    bot_manager = TelegramBotManager(settings.telegram_bot.token.get_secret_value())
    await bot_manager.start()
    return bot_manager
