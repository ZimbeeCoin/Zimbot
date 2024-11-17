# src/zimbot/core/integrations/livekit/client/livekit_client.py

import logging
from typing import Any, Dict, Optional

from livekit import RoomServiceClient

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError

logger = logging.getLogger(__name__)


class LiveKitManager:
    def __init__(self, api_key: str, api_secret: str, host: str):
        """
        Initialize the LiveKitManager.

        Args:
            api_key (str): LiveKit API key.
            api_secret (str): LiveKit API secret.
            host (str): LiveKit server host URL.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = host
        self.client: Optional[RoomServiceClient] = None
        self._healthy: bool = False

    async def start(self):
        """Initialize LiveKit client."""
        try:
            self.client = RoomServiceClient(
                host=self.host, api_key=self.api_key, api_secret=self.api_secret
            )
            # Optionally, perform a health check or fetch initial data
            self._healthy = True
            logger.info("LiveKitManager initialized successfully.")
        except Exception as e:
            raise IntegrationError(f"Failed to initialize LiveKit: {e}") from e

    async def shutdown(self):
        """Cleanup LiveKit client resources."""
        if self.client:
            await self.client.close()
            logger.info("LiveKit client closed.")
        self._healthy = False

    def is_healthy(self) -> bool:
        """Check if LiveKit client is healthy."""
        return self._healthy

    async def create_room(self, room_name: str) -> Dict[str, Any]:
        """
        Create a new LiveKit room.

        Args:
            room_name (str): Name of the room to create.

        Returns:
            Dict[str, Any]: Details of the created room.
        """
        if not self.client:
            raise IntegrationError("LiveKit client is not initialized.")
        try:
            room = await self.client.create_room(room_name)
            logger.info(f"Created LiveKit room: {room.name}")
            return room.dict()
        except Exception as e:
            logger.error(f"Failed to create LiveKit room '{room_name}': {e}")
            raise IntegrationError(f"Failed to create LiveKit room: {e}") from e

    async def delete_room(self, room_name: str):
        """
        Delete an existing LiveKit room.

        Args:
            room_name (str): Name of the room to delete.
        """
        if not self.client:
            raise IntegrationError("LiveKit client is not initialized.")
        try:
            await self.client.delete_room(room_name)
            logger.info(f"Deleted LiveKit room: {room_name}")
        except Exception as e:
            logger.error(f"Failed to delete LiveKit room '{room_name}': {e}")
            raise IntegrationError(f"Failed to delete LiveKit room: {e}") from e

    # Add more methods as needed to interact with LiveKit
