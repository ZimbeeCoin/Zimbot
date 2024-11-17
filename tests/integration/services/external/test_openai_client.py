# tests/test_openai_client.py

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from core.secrets.secrets_manager import MissingSecretError, SecretsManager

from zimbot.core.integrations.openai.config import OpenAIClient, OpenAIServiceAccount


@pytest.fixture
def service_account():
    return OpenAIServiceAccount(
        index=1,
        name="TestAccount",
        organization_id="org-test",
        secrets_manager=MagicMock(),
    )


@pytest.fixture
def openai_client(service_account):
    return OpenAIClient(service_account, service_account.secrets_manager)


@pytest.mark.asyncio
async def test_initialize_secrets_success(openai_client, service_account):
    service_account.secrets_manager.get_secret = MagicMock(
        side_effect=["test_api_key", "test_org_id"]
    )
    with patch("openai.ChatCompletion.acreate") as mock_acreate:
        await openai_client.initialize_secrets()
        service_account.secrets_manager.get_secret.assert_called_with(
            "OPENAI_API_SECRET_KEY1"
        )
        service_account.secrets_manager.get_secret.assert_called_with(
            "OPENAI_ORGANIZATION_ID1"
        )
        assert openai.api_key == "test_api_key"
        assert openai.organization == "test_org_id"


@pytest.mark.asyncio
async def test_initialize_secrets_missing_secret(openai_client, service_account):
    service_account.secrets_manager.get_secret = MagicMock(
        side_effect=MissingSecretError("OPENAI_API_SECRET_KEY1")
    )
    with pytest.raises(MissingSecretError):
        await openai_client.initialize_secrets()


@pytest.mark.asyncio
async def test_create_completion_success(openai_client):
    openai_client.get_model = MagicMock(return_value="gpt-4")
    with patch("openai.ChatCompletion.acreate") as mock_acreate:
        mock_acreate.return_value = {
            "choices": [{"text": "test response"}],
            "usage": {"total_tokens": 10},
        }
        response = await openai_client.create_completion(prompt="Hello")
        assert response["choices"][0]["text"] == "test response"
        openai_client.secrets_manager.get_secret.assert_not_called()


@pytest.mark.asyncio
async def test_create_completion_rate_limit_error(openai_client):
    openai_client.get_model = MagicMock(return_value="gpt-4")
    with patch(
        "openai.ChatCompletion.acreate",
        side_effect=openai.error.RateLimitError("Rate limit exceeded"),
    ) as mock_acreate:
        with patch.object(openai_client, "switch_model") as mock_switch_model:
            with pytest.raises(openai.error.RateLimitError):
                await openai_client.create_completion(prompt="Hello")
            assert mock_switch_model.called
