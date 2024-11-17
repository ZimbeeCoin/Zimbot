from core.config import config


class AssistantClient:
    """OpenAI assistant implementation."""

    def __init__(self):
        self.config = config.get("openai")
