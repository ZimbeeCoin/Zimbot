# tests/integration/secrets/test_secrets_manager.py

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from zimbot.core.secrets.alerting import Alerting
from zimbot.core.secrets.aws_client_manager import AWSSecretsClientManager
from zimbot.core.secrets.caching import Caching
from zimbot.core.secrets.exceptions import MissingSecretError
from zimbot.core.secrets.health_check import SecretsManagerHealthCheck
from zimbot.core.secrets.metrics import cache_hit_counter, cache_miss_counter
from zimbot.core.secrets.redis_client_manager import RedisClientManager
from zimbot.core.secrets.rotation import SecretsRotator
from zimbot.core.secrets.secrets_manager import SecretsManager
from zimbot.core.secrets.secrets_retriever import SecretsRetriever


@pytest.mark.asyncio
async def test_secrets_manager_get_secret_success():
    # Mock AWS client
    aws_client_manager = AWSSecretsClientManager(use_async=True)
    mock_async_client = AsyncMock()
    mock_async_client.get_secret_value.return_value = {
        "SecretString": '{"TEST_SECRET": "test_value"}'
    }
    aws_client_manager.get_async_client = AsyncMock(return_value=mock_async_client)

    # Mock Redis client
    redis_client_manager = RedisClientManager(use_async=True)
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    redis_client_manager.create_async_redis_pool = AsyncMock(
        return_value=mock_redis_client
    )

    # Initialize other components
    caching = Caching(
        redis_enabled=True,
        redis_available=True,
        cache_hit_counter=cache_hit_counter,
        cache_miss_counter=cache_miss_counter,
    )
    alerting = Alerting(
        email_alerts=[],
        slack_webhooks=[],
        webhook_urls=[],
        smtp_config={},
    )

    # Instantiate SecretsManager
    secrets_manager = SecretsManager(
        use_async=True,
        use_secrets_manager=True,
        aws_region="us-east-1",
        redis_url="redis://localhost:6379/0",
        alerting=alerting,
        secret_names=["TEST_SECRET"],
    )

    # Mock cache miss and successful retrieval
    mock_redis_client.get.return_value = None  # Simulate cache miss

    # Run within async context
    async with secrets_manager:
        secret = await secrets_manager.get_secret("TEST_SECRET")
        assert secret == "test_value"
