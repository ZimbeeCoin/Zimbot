# tests/unit/secrets/test_secrets_retriever.py

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from botocore.exceptions import (  # Import ClientError for handling AWS errors
    ClientError,
)

from zimbot.core.secrets.alerting import Alerting
from zimbot.core.secrets.aws_client_manager import AWSSecretsClientManager
from zimbot.core.secrets.caching import Caching
from zimbot.core.secrets.exceptions import MissingSecretError
from zimbot.core.secrets.secrets_retriever import SecretsRetriever


@pytest.fixture
def mock_aws_client_manager():
    return AWSSecretsClientManager()


@pytest.fixture
def mock_caching():
    return Caching()


@pytest.fixture
def mock_alerting():
    return Alerting(
        email_alerts=[],
        slack_webhooks=[],
        webhook_urls=[],
        smtp_config={},
    )


@pytest.mark.asyncio
async def test_get_secret_async_success(
    mock_aws_client_manager, mock_caching, mock_alerting
):
    # Mock AWS client
    mock_client = AsyncMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": '{"TEST_SECRET": "test_value"}'
    }
    mock_aws_client_manager.get_async_client = AsyncMock(return_value=mock_client)

    retriever = SecretsRetriever(
        aws_client_manager=mock_aws_client_manager,
        caching=mock_caching,
        alerting=mock_alerting,
        metrics=None,
    )

    # Retrieve secret and check result
    secret = await retriever.get_secret_async("TEST_SECRET")
    assert secret == "test_value"
    mock_caching.set_cached_secret.assert_called_with("TEST_SECRET", "test_value")


@pytest.mark.asyncio
async def test_get_secret_async_missing_secret(
    mock_aws_client_manager, mock_caching, mock_alerting
):
    # Mock AWS client to raise ResourceNotFoundException
    mock_client = AsyncMock()
    error_response = {
        "Error": {
            "Code": "ResourceNotFoundException",
            "Message": "Secrets Manager can't find the specified secret.",
        }
    }
    mock_client.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )
    mock_aws_client_manager.get_async_client = AsyncMock(return_value=mock_client)

    retriever = SecretsRetriever(
        aws_client_manager=mock_aws_client_manager,
        caching=mock_caching,
        alerting=mock_alerting,
        metrics=None,
    )

    # Expect MissingSecretError to be raised for a missing secret
    with pytest.raises(MissingSecretError):
        await retriever.get_secret_async("NON_EXISTENT_SECRET")
