# src/tests/test_config_loading.py

import logging
import unittest
from unittest.mock import patch

from zimbot.core.config.aws_config import aws_settings
from zimbot.core.secrets.aws_client_manager import AWSClientManager
from zimbot.core.secrets.environment import EnvironmentSecretsManager
from zimbot.core.secrets.exceptions import MissingSecretError

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestConfigLoading(unittest.TestCase):

    def setUp(self):
        # Set up any necessary initialization before each test
        logger.info("Setting up test environment.")

    @patch.dict(
        "os.environ",
        {
            "USE_SECRETS_MANAGER": "false",
            "AWS_REGION": "us-west-2",
            "AWS_ACCESS_KEY_ID": "env_access_key",
            "AWS_SECRET_ACCESS_KEY": "env_secret_key",
            "JWT_SECRET_KEY": "env_jwt_secret_key",
        },
        clear=True,
    )
    def test_load_from_env(self):
        logger.info("Testing environment variable loading.")

        # Verify aws_settings reflects .env values
        self.assertFalse(aws_settings.is_aws_enabled())
        self.assertEqual(aws_settings.region, "us-west-2")
        self.assertEqual(
            aws_settings.access_key_id.get_secret_value(), "env_access_key"
        )
        self.assertEqual(
            aws_settings.secret_access_key.get_secret_value(), "env_secret_key"
        )
        self.assertIsNone(aws_settings.session_token)  # If not set

        # Test secret retrieval from environment
        env_secrets_manager = EnvironmentSecretsManager()
        secret = env_secrets_manager.get_secret("JWT_SECRET_KEY")
        self.assertEqual(secret, "env_jwt_secret_key")

    @patch.dict(
        "os.environ",
        {
            "USE_SECRETS_MANAGER": "true",
            "AWS_REGION": "us-west-2",
            "AWS_ACCESS_KEY_ID": "sm_access_key",
            "AWS_SECRET_ACCESS_KEY": "sm_secret_key",
            "AWS_SESSION_TOKEN": "sm_session_token",
        },
        clear=True,
    )
    @patch.object(AWSClientManager, "get_secret_sync", return_value="sm_jwt_secret_key")
    def test_load_from_secrets_manager(self, mock_get_secret_sync):
        logger.info("Testing AWS Secrets Manager loading.")

        # Verify aws_settings with AWS Secrets Manager enabled
        self.assertTrue(aws_settings.is_aws_enabled())
        self.assertEqual(aws_settings.region, "us-west-2")
        self.assertEqual(aws_settings.access_key_id.get_secret_value(), "sm_access_key")
        self.assertEqual(
            aws_settings.secret_access_key.get_secret_value(), "sm_secret_key"
        )
        self.assertEqual(
            aws_settings.session_token.get_secret_value(), "sm_session_token"
        )

        # Initialize AWSClientManager only if needed
        aws_client_manager = (
            AWSClientManager() if aws_settings.is_aws_enabled() else None
        )

        # Test secret retrieval from AWS Secrets Manager
        env_secrets_manager = EnvironmentSecretsManager(
            aws_client_manager=aws_client_manager
        )
        secret = env_secrets_manager.get_secret("JWT_SECRET_KEY")
        self.assertEqual(secret, "sm_jwt_secret_key")

    @patch.dict(
        "os.environ",
        {
            "USE_SECRETS_MANAGER": "false",
            "AWS_REGION": "us-west-2",
            "AWS_ACCESS_KEY_ID": "env_access_key",
            "AWS_SECRET_ACCESS_KEY": "env_secret_key",
        },
        clear=True,
    )
    def test_missing_secret_in_env(self):
        logger.info("Testing missing secret retrieval from environment variables.")

        # Verify aws_settings without AWS Secrets Manager
        self.assertFalse(aws_settings.is_aws_enabled())

        # Test missing secret error handling
        env_secrets_manager = EnvironmentSecretsManager()
        with self.assertRaises(MissingSecretError):
            env_secrets_manager.get_secret("NON_EXISTENT_SECRET")

    def tearDown(self):
        # Clean up if necessary after each test
        logger.info("Tearing down test environment.")


if __name__ == "__main__":
    unittest.main()
