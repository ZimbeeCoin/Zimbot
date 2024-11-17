# tests/integrations/openai/test_config.py

import os
from unittest.mock import patch

import pytest

from zimbot.core.integrations.openai.config import create_openai_service_config
from zimbot.core.integrations.openai.exceptions import SecretsManagerError


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_openai_config_loading(mock_get_secret):
    mock_get_secret.return_value = {
        "API_KEY": "test-secret-key",
        "ORGANIZATION_ID": "org-test",
        "PROJECT": "TestProject",
    }
    config = create_openai_service_config("TestSecrets", "OPENAI_TEST_")
    assert config.api_key.get_secret_value() == "test-secret-key"
    assert config.organization_id.get_secret_value() == "org-test"
    assert config.project == "TestProject"
    assert config.base_url == "https://api.openai.com/v1/"
    assert config.api_version == "v1"


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_production_requirements(mock_get_secret):
    mock_get_secret.return_value = {
        "API_KEY": "prod-secret-key",
        "DEFAULT_MODEL": "gpt-4",
    }
    os.environ["ENV"] = "production"
    config = create_openai_service_config("ProdSecrets", "OPENAI_PROD_")
    assert config.api_key.get_secret_value() == "prod-secret-key"
    assert config.default_model == "gpt-4"
    assert not config.debug_mode


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_missing_api_key_in_production(mock_get_secret):
    mock_get_secret.return_value = {}
    os.environ["ENV"] = "production"
    with pytest.raises(ValueError, match="api_key must be provided in production."):
        create_openai_service_config("MissingAPIKeySecrets", "OPENAI_MISSING_")


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_invalid_default_model_in_production(mock_get_secret):
    mock_get_secret.return_value = {
        "API_KEY": "prod-secret-key",
        "DEFAULT_MODEL": "gpt-5",
    }
    os.environ["ENV"] = "production"
    with pytest.raises(
        ValueError,
        match="default_model must be 'gpt-4' or 'gpt-3.5' in production.",
    ):
        create_openai_service_config("InvalidModelSecrets", "OPENAI_INVALID_")


@patch("src.core.integrations.openai.secrets_manager.get_secret")
def test_debug_mode_in_production(mock_get_secret):
    mock_get_secret.return_value = {
        "API_KEY": "prod-secret-key",
        "DEFAULT_MODEL": "gpt-4",
        "DEBUG_MODE": True,
    }
    os.environ["ENV"] = "production"
    with pytest.raises(ValueError, match="debug_mode must be False in production."):
        create_openai_service_config("DebugModeSecrets", "OPENAI_DEBUG_")
