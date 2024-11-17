# tests/unit/core/integrations/openai/test_config.py

import os
from unittest.mock import patch

import pytest

from zimbot.core.integrations.openai.config import create_openai_service_config
from zimbot.core.integrations.openai.exceptions import SecretsManagerError


@pytest.fixture
def set_env(monkeypatch):
    """Fixture to set and clear environment variables for each test."""
    monkeypatch.setenv(
        "ENV_FILE", ".env.test"
    )  # Example, in case specific env file needed
    yield monkeypatch  # Provides the monkeypatch instance for use in tests
    monkeypatch.delenv("ENV", raising=False)  # Ensure "ENV" is reset after each test


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_openai_config_loading(mock_get_secret, set_env):
    mock_get_secret.return_value = {
        "api_key": "test-secret-key",
        "organization_id": "org-test",
        "project": "TestProject",
    }
    config = create_openai_service_config("TestSecrets", "OPENAI_TEST_")

    # Basic assertions to check if values are correctly set
    assert config.api_key.get_secret_value() == "test-secret-key"
    assert config.organization_id.get_secret_value() == "org-test"
    assert config.project == "TestProject"

    # Check default values
    assert config.base_url == "https://api.openai.com/v1/"
    assert config.api_version == "v1"


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_production_requirements(mock_get_secret, set_env):
    mock_get_secret.return_value = {
        "api_key": "prod-secret-key",
        "default_model": "gpt-4",
    }
    set_env.setenv("ENV", "production")  # Use monkeypatch to set the environment

    config = create_openai_service_config("ProdSecrets", "OPENAI_PROD_")

    # Check if production settings are enforced correctly
    assert config.api_key.get_secret_value() == "prod-secret-key"
    assert config.default_model == "gpt-4"
    assert not config.debug_mode  # Ensure debug_mode is disabled by default


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_missing_api_key_in_production(mock_get_secret, set_env):
    mock_get_secret.return_value = {}
    set_env.setenv("ENV", "production")

    # Expect an error if the api_key is missing in production
    with pytest.raises(ValueError, match="api_key must be provided in production."):
        create_openai_service_config("MissingAPIKeySecrets", "OPENAI_MISSING_")


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_invalid_default_model_in_production(mock_get_secret, set_env):
    mock_get_secret.return_value = {
        "api_key": "prod-secret-key",
        "default_model": "gpt-5",
    }
    set_env.setenv("ENV", "production")

    # Expect an error if an invalid model is set in production
    with pytest.raises(
        ValueError,
        match="default_model must be 'gpt-4' or 'gpt-3.5' in production.",
    ):
        create_openai_service_config("InvalidModelSecrets", "OPENAI_INVALID_")


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_debug_mode_in_production(mock_get_secret, set_env):
    mock_get_secret.return_value = {
        "api_key": "prod-secret-key",
        "default_model": "gpt-4",
        "debug_mode": True,
    }
    set_env.setenv("ENV", "production")

    # Expect an error if debug_mode is enabled in production
    with pytest.raises(ValueError, match="debug_mode must be False in production."):
        create_openai_service_config("DebugModeSecrets", "OPENAI_DEBUG_")
