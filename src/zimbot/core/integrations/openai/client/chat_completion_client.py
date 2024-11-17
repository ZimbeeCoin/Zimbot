# src/core/integrations/openai/chat_completion_client.py

from typing import Any, AsyncIterator, Dict, List, Optional, Union

import sentry_sdk
from core.utils.logger import get_logger
from pydantic import ValidationError

from .base_client import OpenAIBaseClient
from .types import ChatCompletionResponse, OpenAIError, StreamEvent

logger = get_logger(__name__)


class ChatCompletionClient(OpenAIBaseClient):
    """Client for handling chat completions."""

    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        max_tokens: Optional[int] = None,
        cancel_event: Optional[asyncio.Event] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[StreamEvent]]:
        """
        Create a chat completion with optional streaming.

        Args:
            messages (List[Dict[str, str]]): List of message dictionaries.
            model (Optional[str]): Model to use. Defaults to the configured default model.
            temperature (float): Sampling temperature. Defaults to 0.7.
            stream (bool): Whether to stream the response. Defaults to False.
            max_tokens (Optional[int]): Maximum number of tokens to generate.
            cancel_event (Optional[asyncio.Event]): Event to signal cancellation of streaming.

        Returns:
            Union[Dict[str, Any], AsyncIterator[StreamEvent]]: Parsed JSON response or a stream of events.
        """
        payload = {
            "model": model or self.config.default_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = await self._make_request(
                "POST",
                "chat/completions",
                data=payload,
                stream=stream,
                cancel_event=cancel_event,
            )
            if stream:
                self.logger.info("Started streaming chat completion")
            else:
                self.logger.info("Completed chat completion")
            return response
        except OpenAIError as oe:
            self.logger.error(f"Failed to create chat completion: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during chat completion: {e}")
            sentry_sdk.capture_exception(e)
            raise OpenAIError(f"Unexpected error: {e}") from e

    async def list_chat_completions(
        self,
        model: Optional[str] = None,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[ChatCompletionResponse]:
        """
        List available chat completions.

        Args:
            model (Optional[str]): Model to filter chat completions.
            limit (int): Number of chat completions to retrieve. Defaults to 20.
            order (str): Order of retrieval ('asc' or 'desc'). Defaults to 'desc'.
            after (Optional[str]): Cursor for pagination.
            before (Optional[str]): Cursor for pagination.

        Returns:
            List[ChatCompletionResponse]: List of chat completion response objects.
        """
        params = {
            "limit": limit,
            "order": order,
        }
        if model:
            params["model"] = model
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        try:
            response = await self._make_request(
                "GET", "chat/completions", params=params
            )
            chat_completions_data = response.get("data", [])
            chat_completions = [
                ChatCompletionResponse(**chat) for chat in chat_completions_data
            ]
            self.logger.info(f"Retrieved {len(chat_completions)} chat completions")
            return chat_completions
        except ValidationError as ve:
            self.logger.error(f"List chat completions validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(
                f"List chat completions data validation failed: {ve}"
            ) from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to list chat completions: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
