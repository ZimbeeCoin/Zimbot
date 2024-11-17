# tests/config/test_config.py

from unittest.mock import patch

import pytest

from src.core.config.config import OpenAIServiceAccount, Settings


# Mock environment variables
@pytest.fixture
def mock_env(monkeypatch):
    # LiveKit
    monkeypatch.setenv("LIVEKIT_NAME", "TestLiveKit")
    monkeypatch.setenv("LIVEKIT_WEBSOCKET_URL", "wss://livekit.test.com")
    monkeypatch.setenv("LIVEKIT_API_KEY", "test_livekit_api_key")
    monkeypatch.setenv("LIVEKIT_SECRET_KEY", "test_livekit_secret_key")
    monkeypatch.setenv("LIVEKIT_SIP_URI", "sip:test@livekit.com")
    monkeypatch.setenv("LIVEKIT_GENERATED_TOKEN", "test_generated_token")

    # OpenAI
    monkeypatch.setenv("OPENAI_NAME1", "PrimaryAssistant")
    monkeypatch.setenv("OPENAI_ORGANIZATION_ID1", "org-123")
    monkeypatch.setenv("OPENAI_API_SECRET_KEY1", "primary_openai_secret_key")
    monkeypatch.setenv("OPENAI_NAME2", "SecondaryAssistant")
    monkeypatch.setenv("OPENAI_ORGANIZATION_ID2", "org-456")
    monkeypatch.setenv("OPENAI_API_SECRET_KEY2", "secondary_openai_secret_key")
    monkeypatch.setenv("OPENAI_DEFAULT_MODEL", "gpt-4o")
    monkeypatch.setenv("OPENAI_BACKUP_MODEL", "gpt-4o-mini")

    # Telegram Bot
    monkeypatch.setenv("TELEGRAM_BOT_NAME", "TestTelegramBot")
    monkeypatch.setenv("TELEGRAM_BOT_USERNAME", "@TestTelegramBot")
    monkeypatch.setenv("TELEGRAM_BOT_API", "test_telegram_bot_api_key")

    # LiveCoinWatch
    monkeypatch.setenv("LIVECOINWATCH_USERNAME1", "user1")
    monkeypatch.setenv("LIVECOINWATCH_EMAIL1", "user1@example.com")
    monkeypatch.setenv("LIVECOINWATCH_API_KEY1", "livecoinwatch_api_key1")
    monkeypatch.setenv("LIVECOINWATCH_USERNAME2", "user2")
    monkeypatch.setenv("LIVECOINWATCH_EMAIL2", "user2@example.com")
    monkeypatch.setenv("LIVECOINWATCH_API_KEY2", "livecoinwatch_api_key2")
    monkeypatch.setenv("LIVECOINWATCH_USERNAME3", "user3")
    monkeypatch.setenv("LIVECOINWATCH_EMAIL3", "user3@example.com")
    monkeypatch.setenv("LIVECOINWATCH_API_KEY3", "livecoinwatch_api_key3")

    # CoinAPI
    monkeypatch.setenv("MARKET_DATA_API", "https://api.coinapi.test/v1/")
    monkeypatch.setenv("EMS_TRADING_API", "https://ems.trading.coinapi.test/")
    monkeypatch.setenv(
        "NODE_AS_A_SERVICE_API", "https://node.as.a.service.coinapi.test/"
    )
    monkeypatch.setenv("FLAT_FILES_API", "https://flat.files.coinapi.test/")
    monkeypatch.setenv("INDEXES_API", "https://indexes.coinapi.test/")

    # Github Tokens
    monkeypatch.setenv("GITHUB_DEVELOPMENT_TOKEN", "github_dev_token")
    monkeypatch.setenv("GITHUB_CICD_TOKEN", "github_cicd_token")
    monkeypatch.setenv("GITHUB_PACKAGE_TOKEN", "github_package_token")
    monkeypatch.setenv("GITHUB_SECURITY_TOKEN", "github_security_token")
    monkeypatch.setenv("GITHUB_ADMIN_TOKEN", "github_admin_token")
    monkeypatch.setenv("GITHUB_ACCOUNT_TOKEN", "github_account_token")

    # JWT
    monkeypatch.setenv("JWT_SECRET_KEY", "test_jwt_secret_key")

    # API Base URL
    monkeypatch.setenv("API_BASE_URL", "http://localhost:8000")

    # Redis
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")

    # Stripe
    monkeypatch.setenv("STRIPE_API_KEY", "test_stripe_api_key")
    monkeypatch.setenv("STRIPE_API_SECRET_KEY", "test_stripe_api_secret_key")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "test_stripe_webhook_secret")

    # Ngrok
    monkeypatch.setenv("NGROK_API_NAME", "TestNgrokAPI")
    monkeypatch.setenv("NGROK_API_KEY", "test_ngrok_api_key")
    monkeypatch.setenv("NGROK_AUTH_TOKEN", "test_ngrok_auth_token")

    # Application Environment
    monkeypatch.setenv("APP_ENV", "development")

    # Environment File
    monkeypatch.setenv("ENV_FILE", ".env")


def test_livekit_settings(mock_env):
    settings = Settings()
    livekit = settings.livekit
    assert livekit.name == "TestLiveKit"
    assert livekit.websocket_url == "wss://livekit.test.com"
    assert livekit.api_key.get_secret_value() == "test_livekit_api_key"
    assert livekit.secret_key.get_secret_value() == "test_livekit_secret_key"
    assert livekit.sip_uri == "sip:test@livekit.com"
    assert livekit.generated_token == "test_generated_token"


def test_openai_settings(mock_env):
    settings = Settings()
    openai = settings.openai
    assert len(openai.service_accounts) == 2
    assert openai.service_accounts[0].name == "PrimaryAssistant"
    assert openai.service_accounts[0].organization_id == "org-123"
    assert (
        openai.service_accounts[0].api_secret_key.get_secret_value()
        == "primary_openai_secret_key"
    )
    assert openai.service_accounts[0].default_model == "gpt-4o"
    assert openai.service_accounts[0].backup_model == "gpt-4o-mini"
    assert openai.service_accounts[1].name == "SecondaryAssistant"
    assert openai.service_accounts[1].organization_id == "org-456"
    assert (
        openai.service_accounts[1].api_secret_key.get_secret_value()
        == "secondary_openai_secret_key"
    )
    assert openai.service_accounts[1].default_model == "gpt-4o"
    assert openai.service_accounts[1].backup_model == "gpt-4o-mini"


def test_telegram_bot_settings(mock_env):
    settings = Settings()
    telegram_bot = settings.telegram_bot
    assert telegram_bot.name == "TestTelegramBot"
    assert telegram_bot.username == "@TestTelegramBot"
    assert telegram_bot.api.get_secret_value() == "test_telegram_bot_api_key"


def test_livecoinwatch_settings(mock_env):
    settings = Settings()
    livecoinwatch = settings.livecoinwatch
    assert livecoinwatch.username1 == "user1"
    assert livecoinwatch.email1 == "user1@example.com"
    assert livecoinwatch.api_key1.get_secret_value() == "livecoinwatch_api_key1"
    assert livecoinwatch.username2 == "user2"
    assert livecoinwatch.email2 == "user2@example.com"
    assert livecoinwatch.api_key2.get_secret_value() == "livecoinwatch_api_key2"
    assert livecoinwatch.username3 == "user3"
    assert livecoinwatch.email3 == "user3@example.com"
    assert livecoinwatch.api_key3.get_secret_value() == "livecoinwatch_api_key3"


def test_coinapi_settings(mock_env):
    settings = Settings()
    coinapi = settings.coinapi
    assert coinapi.market_data_api == "https://api.coinapi.test/v1/"
    assert coinapi.ems_trading_api == "https://ems.trading.coinapi.test/"
    assert coinapi.node_as_a_service_api == "https://node.as.a.service.coinapi.test/"
    assert coinapi.flat_files_api == "https://flat.files.coinapi.test/"
    assert coinapi.indexes_api == "https://indexes.coinapi.test/"


def test_github_token_settings(mock_env):
    settings = Settings()
    github = settings.github_tokens
    assert github.development_token.get_secret_value() == "github_dev_token"
    assert github.cicd_token.get_secret_value() == "github_cicd_token"
    assert github.package_token.get_secret_value() == "github_package_token"
    assert github.security_token.get_secret_value() == "github_security_token"
    assert github.admin_token.get_secret_value() == "github_admin_token"
    assert github.account_token.get_secret_value() == "github_account_token"


def test_jwt_settings(mock_env):
    settings = Settings()
    jwt = settings.jwt
    assert jwt.secret_key.get_secret_value() == "test_jwt_secret_key"


def test_api_base_url_settings(mock_env):
    settings = Settings()
    api = settings.api_base_url
    assert api.api_base_url == "http://localhost:8000"


def test_redis_settings(mock_env):
    settings = Settings()
    redis = settings.redis
    assert redis.host == "localhost"
    assert redis.port == 6379
    assert redis.db == 0


def test_stripe_settings(mock_env):
    settings = Settings()
    stripe = settings.stripe
    assert stripe.api_key.get_secret_value() == "test_stripe_api_key"
    assert stripe.api_secret_key.get_secret_value() == "test_stripe_api_secret_key"
    assert stripe.webhook_secret.get_secret_value() == "test_stripe_webhook_secret"


def test_ngrok_settings(mock_env):
    settings = Settings()
    ngrok = settings.ngrok
    assert ngrok.api_name == "TestNgrokAPI"
    assert ngrok.api_key.get_secret_value() == "test_ngrok_api_key"
    assert ngrok.auth_token.get_secret_value() == "test_ngrok_auth_token"
