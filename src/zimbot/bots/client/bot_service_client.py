from typing import List, Optional

from bots.types.types import BotCreate, BotModel
from core.config import settings


class BotClient:
    """Client for interacting with Telegram Bot API."""

    def __init__(self) -> None:
        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the Telegram client."""
        # Add SDK-specific initialization here
        pass

    async def create_bot(self, data: BotCreate) -> BotModel:
        """Create a new bot."""
        raise NotImplementedError

    async def list_bots(self, limit: int = 20) -> List[BotModel]:
        """List available bots."""
        raise NotImplementedError
