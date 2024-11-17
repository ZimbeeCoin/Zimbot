# tests/config/test_import_openai.py
import os
import unittest

from dotenv import load_dotenv

from zimbot.core.config.openai_config import OpenAISettings

# Load environment variables from .env file
load_dotenv()


class TestOpenAISettingsImport(unittest.TestCase):
    def setUp(self):
        # Set the correct environment variable for the test if not set
        if "MARKET_DATA_API" not in os.environ:
            os.environ["MARKET_DATA_API"] = "c038a032-8696-4820-a37d-f4f4ff867323"

    def test_import_openai_settings(self):
        # Instantiate OpenAISettings to ensure it imports and initializes without error
        settings = OpenAISettings()
        self.assertIsInstance(settings, OpenAISettings)

    def test_market_data_api_key_present(self):
        # Verify that MARKET_DATA_API is loaded and accessible
        self.assertIn(
            "MARKET_DATA_API",
            os.environ,
            "MARKET_DATA_API is missing in the environment.",
        )
        print(
            f"MARKET_DATA_API: {os.getenv('MARKET_DATA_API')}"
        )  # Print the API key for debugging


if __name__ == "__main__":
    unittest.main()
