from typing import Optional

from pydantic import Field

from .base import BaseConfig


class DebugSettings(BaseConfig):
    """Settings for debug mode and related configurations."""

    debug_mode: bool = Field(
        default=False,
        description="Enable or disable debug mode."
    )
    reload: bool = Field(
        default=False,
        description="Enable or disable auto-reloading during development."
    )
    log_level_override: Optional[str] = Field(
        default=None,
        description="Override log level for debugging purposes."
    )

    # Use the correct method to extend model_config for Pydantic v2
    model_config = {
        **BaseConfig.model_config,
        "env_prefix": "DEBUG_",
    }
