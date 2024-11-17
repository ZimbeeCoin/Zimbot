from typing import List, Optional

from core.config import settings
from rooms.types.types import RoomCreate, RoomModel


class RoomClient:
    """Client for interacting with LiveKit Room API."""

    def __init__(self) -> None:
        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the LiveKit client."""
        # Add SDK-specific initialization here
        pass

    async def create_room(self, data: RoomCreate) -> RoomModel:
        """Create a new room."""
        raise NotImplementedError

    async def list_rooms(self, limit: int = 20) -> List[RoomModel]:
        """List available rooms."""
        raise NotImplementedError
