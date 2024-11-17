# src/zimbot/core/integrations/openai/service_manager.py

import asyncio
from typing import Any, Dict, Optional

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions.exceptions import IntegrationError
from zimbot.core.integrations.openai.clients import (  # Assuming you have an OpenAIClient
    OpenAIClient,
)


class OpenAIServiceManager:
    def __init__(self, service_accounts: Dict[str, Any]):
        self.service_accounts = service_accounts
        self.clients: Dict[str, OpenAIClient] = {}
        self.healthy = False

    async def start(self):
        """Initialize OpenAI clients based on service accounts."""
        try:
            for account_name, config in self.service_accounts.items():
                client = OpenAIClient(config)
                await client.connect()
                self.clients[account_name] = client
            self.healthy = True
            print("OpenAIServiceManager initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize OpenAIServiceManager: {e}")
            self.healthy = False
            raise IntegrationError(
                f"Failed to initialize OpenAIServiceManager: {e}"
            ) from e

    def is_healthy(self) -> bool:
        """Check if all OpenAI clients are healthy."""
        return self.healthy and all(
            client.is_healthy() for client in self.clients.values()
        )

    async def shutdown(self):
        """Shutdown all OpenAI clients."""
        for client in self.clients.values():
            await client.disconnect()
        self.healthy = False
        print("OpenAIServiceManager shutdown completed.")

    async def create_completion(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Create a completion using a specified OpenAI client."""
        if not self.clients:
            raise IntegrationError("No OpenAI clients available.")
        client = next(iter(self.clients.values()))
        return await client.create_completion(prompt, max_tokens)
