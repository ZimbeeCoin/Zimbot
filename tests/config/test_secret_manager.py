# tests/test_secrets_manager.py

import asyncio
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from src.core.config.secrets_manager import (
    MaxRetriesExceededError,
    MissingSecretError,
    SecretsManager,
)


@pytest.fixture
def secrets_manager_sync():
    return SecretsManager(use_async=False)


@pytest.fixture
def secrets_manager_async():
    return SecretsManager(use_async=True)


def test_get_secret_sync_environment_fallback(secrets_manager_sync):
    with patch.dict(os.environ, {"TEST_SECRET": "test_value"}):
        secret = secrets_manager_sync.get_secret_sync("TEST_SECRET")
        assert secret == "test_value"


def test_get_secret_sync_missing_secret(secrets_manager_sync):
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(MissingSecretError):
            secrets_manager_sync.get_secret_sync("MISSING_SECRET")


@pytest.mark.asyncio
async def test_get_secret_async_environment_fallback(secrets_manager_async):
    with patch.dict(os.environ, {"TEST_SECRET": "test_value"}):
        secret = await secrets_manager_async.get_secret_async("TEST_SECRET")
        assert secret == "test_value"


@pytest.mark.asyncio
async def test_get_secret_async_missing_secret(secrets_manager_async):
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(MissingSecretError):
            await secrets_manager_async.get_secret_async("MISSING_SECRET")


# Mock AWS Secrets Manager responses
@pytest.mark.asyncio
async def test_get_secret_async_from_aws(secrets_manager_async):
    with patch("aioboto3.Session.client") as mock_client:
        mock_response = {"SecretString": json.dumps({"TEST_SECRET_AWS": "aws_value"})}
        mock_client.return_value.__aenter__.return_value.get_secret_value = MagicMock(
            return_value=mock_response
        )
        secret = await secrets_manager_async.get_secret_async("TEST_SECRET_AWS")
        assert secret == "aws_value"


def test_get_secret_sync_from_aws(secrets_manager_sync):
    with patch("boto3.client") as mock_client:
        mock_response = {"SecretString": json.dumps({"TEST_SECRET_AWS": "aws_value"})}
        mock_instance = mock_client.return_value
        mock_instance.get_secret_value.return_value = mock_response
        secret = secrets_manager_sync.get_secret_sync("TEST_SECRET_AWS")
        assert secret == "aws_value"


def test_max_retries_exceeded_sync(secrets_manager_sync):
    with patch("boto3.client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "InternalServiceErrorException"}},
            "get_secret_value",
        )
        with pytest.raises(MaxRetriesExceededError):
            secrets_manager_sync.get_secret_sync("TEST_SECRET_FAIL")


@pytest.mark.asyncio
async def test_max_retries_exceeded_async(secrets_manager_async):
    with patch("aioboto3.Session.client") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "InternalServiceErrorException"}},
            "get_secret_value",
        )
        with pytest.raises(MaxRetriesExceededError):
            await secrets_manager_async.get_secret_async("TEST_SECRET_FAIL")
