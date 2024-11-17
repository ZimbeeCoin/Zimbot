# src/zimbot/assistants/client/assistant_manager_client.py

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp

from zimbot.core.config.config import Config
from zimbot.core.integrations.openai.types import (
    AssistantObject,
    FileObject,
    MessageObject,
    RunObject,
    ThreadObject,
)


@dataclass
class AssistantClient:
    """Client for interacting with OpenAI's Assistant API"""

    api_key: str
    organization_id: Optional[str] = None
    base_url: str = "https://api.openai.com/v1"

    def __init__(self, config: Config):
        """Initialize the client with configuration"""
        self.api_key = config.openai.api_key
        self.organization_id = config.openai.organization_id
        self.base_url = config.openai.base_url or self.base_url
        self.session = None
        self.project_id = config.openai.project_id  # Added project ID for scoped access

    async def __aenter__(self):
        """Setup async context manager"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "assistants=v2",
                **(
                    {"OpenAI-Organization": self.organization_id}
                    if self.organization_id
                    else {}
                ),
                **({"OpenAI-Project": self.project_id} if self.project_id else {}),
            }
        )
        if self.organization_id:
            self.session.headers.update({"OpenAI-Organization": self.organization_id})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async context manager"""
        if self.session:
            await self.session.close()

    async def create_assistant(
        self,
        model: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AssistantObject:
        """Create a new assistant"""
        payload = {
            "model": model,
            **({"name": name} if name else {}),
            **({"description": description} if description else {}),
            **({"instructions": instructions} if instructions else {}),
            **({"tools": tools} if tools else {}),
            **({"file_ids": file_ids} if file_ids else {}),
            **({"metadata": metadata} if metadata else {}),
        }

        async with self.session.post(
            f"{self.base_url}/assistants", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def retrieve_assistant(self, assistant_id: str) -> AssistantObject:
        """Retrieve an assistant by ID"""
        async with self.session.get(
            f"{self.base_url}/assistants/{assistant_id}"
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def modify_assistant(
        self,
        assistant_id: str,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AssistantObject:
        """Modify an existing assistant"""
        payload = {
            **({"model": model} if model else {}),
            **({"name": name} if name else {}),
            **({"description": description} if description else {}),
            **({"instructions": instructions} if instructions else {}),
            **({"tools": tools} if tools else {}),
            **({"file_ids": file_ids} if file_ids else {}),
            **({"metadata": metadata} if metadata else {}),
        }

        async with self.session.post(
            f"{self.base_url}/assistants/{assistant_id}", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def delete_assistant(self, assistant_id: str) -> bool:
        """Delete an assistant"""
        async with self.session.delete(
            f"{self.base_url}/assistants/{assistant_id}"
        ) as resp:
            resp.raise_for_status()
            result = await resp.json()
            return result.get("deleted", False)

    async def list_assistants(
        self,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List available assistants"""
        params = {
            "limit": limit,
            "order": order,
            **({"after": after} if after else {}),
            **({"before": before} if before else {}),
        }

        async with self.session.get(
            f"{self.base_url}/assistants", params=params
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def create_thread(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ThreadObject:
        """Create a new thread"""
        payload = {
            **({"messages": messages} if messages else {}),
            **({"metadata": metadata} if metadata else {}),
        }

        async with self.session.post(f"{self.base_url}/threads", json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def create_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> MessageObject:
        """Create a new message in a thread"""
        payload = {
            "role": role,
            "content": content,
            **({"file_ids": file_ids} if file_ids else {}),
            **({"metadata": metadata} if metadata else {}),
        }

        async with self.session.post(
            f"{self.base_url}/threads/{thread_id}/messages", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def create_run(
        self,
        thread_id: str,
        assistant_id: str,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> RunObject:
        """Create a new run for a thread"""
        payload = {
            "assistant_id": assistant_id,
            **({"model": model} if model else {}),
            **({"instructions": instructions} if instructions else {}),
            **({"tools": tools} if tools else {}),
            **({"metadata": metadata} if metadata else {}),
        }

        async with self.session.post(
            f"{self.base_url}/threads/{thread_id}/runs", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def retrieve_run(self, thread_id: str, run_id: str) -> RunObject:
        """Retrieve a run by ID"""
        async with self.session.get(
            f"{self.base_url}/threads/{thread_id}/runs/{run_id}"
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def monitor_run(
        self, thread_id: str, run_id: str, polling_interval: float = 1.0
    ) -> RunObject:
        """Monitor a run until it completes or fails"""
        while True:
            run = await self.retrieve_run(thread_id, run_id)
            if run["status"] in [
                "completed",
                "failed",
                "cancelled",
                "expired",
            ]:
                return run
            await asyncio.sleep(polling_interval)

    async def submit_tool_outputs(
        self,
        thread_id: str,
        run_id: str,
        tool_outputs: List[Dict[str, str]],
    ) -> RunObject:
        """Submit tool outputs for a run that requires action"""
        payload = {"tool_outputs": tool_outputs}

        async with self.session.post(
            f"{self.base_url}/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def list_messages(
        self,
        thread_id: str,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List messages in a thread"""
        params = {
            "limit": limit,
            "order": order,
            **({"after": after} if after else {}),
            **({"before": before} if before else {}),
        }

        async with self.session.get(
            f"{self.base_url}/threads/{thread_id}/messages", params=params
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
