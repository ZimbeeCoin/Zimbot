from core.config import config


class RoomClient:
    """LiveKit room implementation."""

    def __init__(self):
        self.config = config.get("livekit")
