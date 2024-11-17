# src/zimbot/core/integrations/openai/assistant_client.py

from typing import Any, Dict, List, Optional

import sentry_sdk
from core.utils.logger import get_logger
from pydantic import ValidationError

from .base_client import OpenAIBaseClient
from .types import Assistant, OpenAIError, Tool

logger = get_logger(__name__)


class AssistantClient(OpenAIBaseClient):
    """Client for managing OpenAI Assistants."""

    async def create_assistant(
        self,
        name: str,
        instructions: str,
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Assistant:
        """
        Create a new assistant with specified parameters.

        Args:
            name (str): Name of the assistant.
            instructions (str): Instructions for the assistant.
            model (Optional[str]): Model to use. Defaults to the configured default model.
            tools (Optional[List[Dict[str, Any]]]): List of tools to integrate with the assistant.
            file_ids (Optional[List[str]]): List of file IDs for assistant access.
            metadata (Optional[Dict[str, Any]]): Additional metadata.

        Returns:
            Assistant: The created assistant object.
        """
        payload = {
            "name": name,
            "instructions": instructions,
            "model": model or self.config.default_model,
            "tools": tools or [],
            "file_ids": file_ids or [],
            "metadata": metadata or {},
        }

        try:
            response = await self._make_request("POST", "assistants", data=payload)
            assistant = Assistant(**response)
            self.logger.info(f"[{assistant.id}] Created assistant: {assistant.name}")
            return assistant
        except ValidationError as ve:
            self.logger.error(f"Assistant validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(f"Assistant data validation failed: {ve}") from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to create assistant: {oe}")
            sentry_sdk.capture_exception(oe)
            raise

    async def retrieve_assistant(self, assistant_id: str) -> Assistant:
        """
        Retrieve an assistant by ID.

        Args:
            assistant_id (str): The ID of the assistant to retrieve.

        Returns:
            Assistant: The retrieved assistant object.
        """
        try:
            response = await self._make_request("GET", f"assistants/{assistant_id}")
            assistant = Assistant(**response)
            self.logger.info(f"[{assistant.id}] Retrieved assistant: {assistant.name}")
            return assistant
        except ValidationError as ve:
            self.logger.error(f"Retrieve assistant validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(
                f"Retrieve assistant data validation failed: {ve}"
            ) from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to retrieve assistant: {oe}")
            sentry_sdk.capture_exception(oe)
            raise

    async def modify_assistant(
        self,
        assistant_id: str,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Assistant:
        """
        Modify an existing assistant.

        Args:
            assistant_id (str): The ID of the assistant to modify.
            name (Optional[str]): New name for the assistant.
            instructions (Optional[str]): New instructions.
            model (Optional[str]): New model.
            tools (Optional[List[Dict[str, Any]]]): New tools.
            file_ids (Optional[List[str]]): New file IDs.
            metadata (Optional[Dict[str, Any]]): New metadata.

        Returns:
            Assistant: The modified assistant object.
        """
        payload = {}
        if name:
            payload["name"] = name
        if instructions:
            payload["instructions"] = instructions
        if model:
            payload["model"] = model
        if tools is not None:
            payload["tools"] = tools
        if file_ids is not None:
            payload["file_ids"] = file_ids
        if metadata is not None:
            payload["metadata"] = metadata

        try:
            response = await self._make_request(
                "POST", f"assistants/{assistant_id}", data=payload
            )
            assistant = Assistant(**response)
            self.logger.info(f"[{assistant.id}] Modified assistant: {assistant.name}")
            return assistant
        except ValidationError as ve:
            self.logger.error(f"Modify assistant validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(f"Modify assistant data validation failed: {ve}") from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to modify assistant: {oe}")
            sentry_sdk.capture_exception(oe)
            raise

    async def delete_assistant(self, assistant_id: str) -> bool:
        """
        Delete an assistant by ID.

        Args:
            assistant_id (str): The ID of the assistant to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = await self._make_request("DELETE", f"assistants/{assistant_id}")
            result = response.get("deleted", False)
            if result:
                self.logger.info(f"[{assistant_id}] Successfully deleted assistant.")
            else:
                self.logger.warning(f"[{assistant_id}] Failed to delete assistant.")
            return result
        except OpenAIError as oe:
            self.logger.error(f"Failed to delete assistant: {oe}")
            sentry_sdk.capture_exception(oe)
            raise

    async def list_assistants(
        self,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Assistant]:
        """
        List available assistants.

        Args:
            limit (int): Number of assistants to retrieve. Defaults to 20.
            order (str): Order of retrieval ('asc' or 'desc'). Defaults to 'desc'.
            after (Optional[str]): Cursor for pagination.
            before (Optional[str]): Cursor for pagination.

        Returns:
            List[Assistant]: List of assistant objects.
        """
        params = {
            "limit": limit,
            "order": order,
        }
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        try:
            response = await self._make_request("GET", "assistants", params=params)
            assistants_data = response.get("data", [])
            assistants = [Assistant(**asst) for asst in assistants_data]
            self.logger.info(f"Retrieved {len(assistants)} assistants")
            return assistants
        except ValidationError as ve:
            self.logger.error(f"List assistants validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(f"List assistants data validation failed: {ve}") from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to list assistants: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
