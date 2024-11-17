from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator


class TelegramBotSettings(BaseModel):
    """Settings for Telegram bot."""

    name: str = Field(
        default="RoboRiches",
        description="Name of the Telegram bot.",
    )
    username: str = Field(
        default="@RoboRich_AI_Bot",
        description="Username of the Telegram bot.",
    )
    api_token: str = Field(
        ...,
        description="Secure API token for the Telegram bot.",
    )
    polling_timeout: int = Field(
        default=60,
        ge=1,
        description="Timeout in seconds for polling updates.",
    )
    worker_count: int = Field(
        default=4,
        ge=1,
        description="Number of worker threads/processes.",
    )
    webhook_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Webhook URL for the Telegram bot in production.",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable or disable debug mode for detailed logging.",
    )

    class Config:
        env_prefix = "TELEGRAM_BOT_"

    @root_validator(pre=True)
    def validate_webhook_and_debug_mode(cls, values):
        """
        Ensure webhook_url is set in production if debug_mode is disabled.
        """
        debug_mode = values.get("debug_mode", False)
        webhook_url = values.get("webhook_url")
        if not debug_mode and not webhook_url:
            raise ValueError("webhook_url must be set when debug_mode is disabled.")
        return values

    def get_sanitized_config(self) -> dict:
        """
        Return a sanitized configuration dictionary,
        excluding sensitive information like `api_token`.
        """
        return {
            "name": self.name,
            "username": self.username,
            "polling_timeout": self.polling_timeout,
            "worker_count": self.worker_count,
            "webhook_url": self.webhook_url,
            "debug_mode": self.debug_mode,
        }
