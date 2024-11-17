import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from zimbot.assistants.internal.manager import AssistantManager
from zimbot.assistants.types.types import (
    AssistantConfiguration,
    RunStatus,
    Tool,
    ToolType,
)
from zimbot.core.config.config import Config


@pytest.fixture
def config():
    mock_config = Mock(spec=Config)
    mock_config.openai.api_key = "test_key"
    mock_config.openai.organization_id = "test_org"
    return mock_config


@pytest.fixture
def mock_assistant_response():
    return {
        "id": "asst_123",
        "object": "assistant",
        "created_at": 1699063290,
        "name": "Test Assistant",
        "description": "Test Description",
        "instructions": "Test Instructions",
        "tools": [],
        "file_ids": [],
        "metadata": {},
    }


@pytest.fixture
def mock_thread_response():
    return {
        "id": "thread_123",
        "object": "thread",
        "created_at": 1699063290,
        "metadata": {},
    }


@pytest.fixture
def mock_run_response():
    return {
        "id": "run_123",
        "object": "thread.run",
        "created_at": 1699063290,
        "thread_id": "thread_123",
        "assistant_id": "asst_123",
        "status": "completed",
        "model": "gpt-4-turbo",
        "tools": [],
        "file_ids": [],
        "metadata": {},
    }


@pytest.fixture
def mock_messages_response():
    return {
        "object": "list",
        "data": [
            {
                "id": "msg_123",
                "object": "thread.message",
                "created_at": 1699063290,
                "thread_id": "thread_123",
                "role": "assistant",
                "content": [{"type": "text", "text": {"value": "Test response"}}],
                "file_ids": [],
                "metadata": {},
            }
        ],
    }


@pytest.mark.asyncio
async def test_create_assistant(config, mock_assistant_response):
    """Test creating a new assistant"""
    with patch("zimbot.assistants.client.client.aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=AsyncMock(
                status=200,
                json=AsyncMock(return_value=mock_assistant_response),
            )
        )

        async with AssistantManager(config) as manager:
            assistant_config = AssistantConfiguration(
                model="gpt-4o",
                name="Test Assistant",
                description="Test Description",
                instructions="Test Instructions",
            )

            assistant = await manager.create_assistant(assistant_config)

            assert assistant["id"] == "asst_123"
            assert assistant["name"] == "Test Assistant"
            assert assistant["model"] == "gpt-4-turbo"


@pytest.mark.asyncio
async def test_get_or_create_thread(config, mock_thread_response):
    """Test creating a new thread"""
    with patch("zimbot.assistants.client.client.aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=AsyncMock(
                status=200, json=AsyncMock(return_value=mock_thread_response)
            )
        )

        async with AssistantManager(config) as manager:
            thread = await manager.get_or_create_thread(
                assistant_id="asst_123", initial_message="Hello"
            )

            assert thread["id"] == "thread_123"
            assert thread["object"] == "thread"


@pytest.mark.asyncio
async def test_process_message(
    config,
    mock_assistant_response,
    mock_thread_response,
    mock_run_response,
    mock_messages_response,
):
    """Test processing a message through an assistant"""
    with patch("zimbot.assistants.client.client.aiohttp.ClientSession") as mock_session:
        mock_post = AsyncMock(
            return_value=AsyncMock(
                status=200,
                json=AsyncMock(
                    side_effect=[
                        mock_thread_response,  # create_message
                        mock_run_response,  # create_run
                    ]
                ),
            )
        )
        mock_get = AsyncMock(
            return_value=AsyncMock(
                status=200,
                json=AsyncMock(
                    side_effect=[
                        mock_run_response,  # retrieve_run
                        mock_messages_response,  # list_messages
                    ]
                ),
            )
        )

        mock_session.return_value.__aenter__.return_value.post = mock_post
        mock_session.return_value.__aenter__.return_value.get = mock_get

        async with AssistantManager(config) as manager:
            messages = await manager.process_message(
                assistant_id="asst_123",
                thread_id="thread_123",
                message="Hello",
            )

            assert len(messages) == 1
            assert messages[0]["role"] == "assistant"
            assert messages[0]["content"][0]["text"]["value"] == "Test response"
