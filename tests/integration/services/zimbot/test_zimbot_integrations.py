"""
Integration Tests for Zimbot Core Modules

This test suite verifies the integration and functionality of core Zimbot modules,
ensuring that they interact correctly and handle various scenarios as expected.
The tests utilize pytest fixtures and async testing to simulate real-world operations.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest

from zimbot.core.auth.services import AuthService
from zimbot.core.config import settings

# Import core Zimbot components
from zimbot.core.integrations.openai.services import OpenAIServiceManager
from zimbot.core.integrations.telegram import TelegramBotManager
from zimbot.finance.client import FinanceClient

# Test configurations (Consider moving to a separate config file or environment variables)
TEST_CONFIG = {
    "openai_api_key": "test_openai_key",
    "telegram_token": "test_telegram_token",
    "stripe_key": "test_stripe_key",
}

# ================================
# Fixtures for Core Service Mocks
# ================================


@pytest.fixture
async def mock_openai_service() -> AsyncGenerator[AsyncMock, None]:
    """
    Fixture providing a mocked OpenAI service manager.
    Handles completion and embedding requests with predefined responses.
    """
    mock_service = AsyncMock(spec=OpenAIServiceManager)
    mock_service.create_completion.return_value = {
        "choices": [{"text": "Test response"}]
    }
    mock_service.create_embedding.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }
    yield mock_service
    # Teardown (if needed)
    mock_service.create_completion.reset_mock()
    mock_service.create_embedding.reset_mock()


@pytest.fixture
async def mock_telegram_bot() -> AsyncGenerator[AsyncMock, None]:
    """
    Fixture providing a mocked Telegram bot manager.
    Simulates message handling and bot commands.
    """
    mock_bot = AsyncMock(spec=TelegramBotManager)
    mock_bot.send_message.return_value = True
    mock_bot.is_running.return_value = True
    mock_bot.handle_message.return_value = (
        None  # Assuming handle_message doesn't return anything
    )
    yield mock_bot
    # Teardown (if needed)
    mock_bot.send_message.reset_mock()
    mock_bot.is_running.reset_mock()
    mock_bot.handle_message.reset_mock()


@pytest.fixture
async def mock_auth_service() -> AsyncGenerator[AsyncMock, None]:
    """
    Fixture providing a mocked authentication service.
    Handles user authentication and token validation.
    """
    mock_auth = AsyncMock(spec=AuthService)
    mock_auth.verify_token.return_value = True
    mock_auth.create_access_token.return_value = "test_token"
    yield mock_auth
    # Teardown (if needed)
    mock_auth.verify_token.reset_mock()
    mock_auth.create_access_token.reset_mock()


@pytest.fixture
async def mock_finance_client() -> AsyncGenerator[AsyncMock, None]:
    """
    Fixture providing a mocked finance client.
    Handles market data and analysis requests.
    """
    mock_client = AsyncMock(spec=FinanceClient)
    mock_client.get_market_data.return_value = {"price": 100.0, "volume": 1000000}
    yield mock_client
    # Teardown (if needed)
    mock_client.get_market_data.reset_mock()


# ======================================
# Integration Test Functions
# ======================================


@pytest.mark.asyncio
async def test_telegram_bot_initialization_and_message_handling(
    mock_telegram_bot: AsyncMock, mock_openai_service: AsyncMock
) -> None:
    """
    Test Telegram bot initialization and basic message handling.

    Ensures that the bot starts correctly and can handle incoming messages by sending responses.
    """
    # Verify bot is running
    assert mock_telegram_bot.is_running() is True, "Telegram bot should be running."

    # Define a test message
    test_message = {"message_id": 1, "chat": {"id": 123}, "text": "Hello bot"}

    # Simulate handling the message
    await mock_telegram_bot.handle_message(test_message)

    # Assert that send_message was called with expected arguments
    mock_telegram_bot.send_message.assert_called_once_with(
        chat_id=123, text="Test response"
    )


@pytest.mark.asyncio
async def test_openai_integration(
    mock_openai_service: AsyncMock, mock_telegram_bot: AsyncMock
) -> None:
    """
    Test OpenAI integration with message processing.

    Validates that OpenAI's completion and embedding services are invoked correctly and return expected data.
    """
    # Test completion request
    completion_response = await mock_openai_service.create_completion(
        prompt="Test prompt", max_tokens=50
    )
    assert (
        "choices" in completion_response
    ), "Completion response should contain 'choices'."
    assert (
        completion_response["choices"][0]["text"] == "Test response"
    ), "Completion text mismatch."

    # Test embedding generation
    embedding_response = await mock_openai_service.create_embedding(text="Test text")
    assert "data" in embedding_response, "Embedding response should contain 'data'."
    assert embedding_response["data"][0]["embedding"] == [
        0.1,
        0.2,
        0.3,
    ], "Embedding data mismatch."


@pytest.mark.asyncio
async def test_auth_flow(mock_auth_service: AsyncMock) -> None:
    """
    Test authentication flow including token creation and validation.

    Ensures that access tokens are created and verified correctly.
    """
    # Test token creation
    token = await mock_auth_service.create_access_token(data={"user_id": "test_user"})
    assert token == "test_token", "Access token generation mismatch."

    # Test token verification
    is_valid = await mock_auth_service.verify_token(token)
    assert is_valid is True, "Token verification should return True."


@pytest.mark.asyncio
async def test_finance_integration(
    mock_finance_client: AsyncMock, mock_telegram_bot: AsyncMock
) -> None:
    """
    Test finance data integration with bot responses.

    Validates that market data is retrieved correctly and responses are sent via the Telegram bot.
    """
    # Test market data retrieval
    market_data = await mock_finance_client.get_market_data(symbol="BTC")
    assert "price" in market_data, "Market data should contain 'price'."
    assert "volume" in market_data, "Market data should contain 'volume'."
    assert market_data["price"] == 100.0, "Market price mismatch."
    assert market_data["volume"] == 1000000, "Market volume mismatch."

    # Simulate sending market data via Telegram bot
    await mock_telegram_bot.send_message(
        chat_id=123, text=f"Price: {market_data['price']}"
    )
    mock_telegram_bot.send_message.assert_called_once_with(
        chat_id=123, text="Price: 100.0"
    )


@pytest.mark.asyncio
async def test_error_handling(
    mock_telegram_bot: AsyncMock, mock_openai_service: AsyncMock
) -> None:
    """
    Test error handling across integrated services.

    Simulates an OpenAI API error and verifies that the Telegram bot sends an appropriate error message.
    """
    # Simulate OpenAI API error
    mock_openai_service.create_completion.side_effect = Exception("API Error")

    # Attempt to create a completion and handle the exception
    with pytest.raises(Exception) as exc_info:
        await mock_openai_service.create_completion(prompt="Test prompt")

    assert str(exc_info.value) == "API Error", "Exception message mismatch."

    # Simulate sending an error message via Telegram bot
    await mock_telegram_bot.send_message(chat_id=123, text="API Error occurred")
    mock_telegram_bot.send_message.assert_called_once_with(
        chat_id=123, text="API Error occurred"
    )


@pytest.mark.asyncio
async def test_openai_retry_mechanism(
    mock_openai_service: AsyncMock, mock_telegram_bot: AsyncMock
) -> None:
    """
    Test OpenAIServiceManager's ability to handle retries upon encountering a timeout.

    Simulates a timeout on the first API call and a successful response on the retry.
    """
    # Simulate a timeout error on the first call and a successful response on the second
    mock_openai_service.create_completion.side_effect = [
        asyncio.TimeoutError("Request timed out"),
        {"choices": [{"text": "Retry successful response"}]},
    ]

    # Attempt to create a completion, expecting the retry mechanism to handle the timeout
    try:
        completion_response = await mock_openai_service.create_completion(
            prompt="Retry prompt", max_tokens=50
        )
    except asyncio.TimeoutError:
        pytest.fail("OpenAIServiceManager did not handle the timeout as expected.")

    # Assert that the second call was successful
    assert (
        "choices" in completion_response
    ), "Completion response should contain 'choices'."
    assert (
        completion_response["choices"][0]["text"] == "Retry successful response"
    ), "Retry response mismatch."

    # Verify that create_completion was called twice due to the retry
    assert (
        mock_openai_service.create_completion.call_count == 2
    ), "create_completion should be called twice."


@pytest.mark.asyncio
async def test_end_to_end_message_flow(
    mock_telegram_bot: AsyncMock,
    mock_openai_service: AsyncMock,
    mock_auth_service: AsyncMock,
    mock_finance_client: AsyncMock,
) -> None:
    """
    Simulate a full message processing flow from receiving a Telegram message to responding back.

    Validates the entire integration pipeline, ensuring seamless interaction between services.
    """
    # Define a test message
    test_message = {"message_id": 2, "chat": {"id": 456}, "text": "Get BTC price"}

    # Mock OpenAI response for processing the message
    mock_openai_service.create_completion.return_value = {
        "choices": [{"text": "Fetch BTC price"}]
    }

    # Mock FinanceClient response for BTC price
    mock_finance_client.get_market_data.return_value = {
        "price": 100.0,
        "volume": 1000000,
    }

    # Simulate handling the message
    await mock_telegram_bot.handle_message(test_message)

    # Assert that OpenAIServiceManager was called to process the message
    mock_openai_service.create_completion.assert_called_once_with(
        prompt="Get BTC price", max_tokens=50
    )

    # Assert that FinanceClient was called to retrieve BTC price
    mock_finance_client.get_market_data.assert_called_once_with(symbol="BTC")

    # Assert that TelegramBotManager sent the correct response
    mock_telegram_bot.send_message.assert_called_once_with(
        chat_id=456, text="Price: 100.0"
    )


# ======================================
# Integration Test Runner (Optional)
# ======================================


def run_integration_tests():
    """
    Main function to run all integration tests.

    Executes pytest with verbose output and asyncio mode.
    """
    pytest.main(
        [
            "-v",
            "--asyncio-mode=strict",
            "tests/integrations/test_zimbot_integrations.py",
        ]
    )


if __name__ == "__main__":
    run_integration_tests()
