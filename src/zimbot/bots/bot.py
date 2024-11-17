from core.config import config


class BotClient:
    """Main bot client implementation."""

    def __init__(self):
        self.config = config.get("telegram")
