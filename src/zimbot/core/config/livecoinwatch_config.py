from typing import Dict

from pydantic import EmailStr, Field, field_validator

from .base import BaseConfig


class LiveCoinWatchSettings(BaseConfig):
    """Settings for LiveCoinWatch API."""

    usernames: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of usernames for LiveCoinWatch accounts.",
    )
    emails: Dict[str, EmailStr] = Field(
        default_factory=dict,
        description="Mapping of emails for LiveCoinWatch accounts.",
    )

    model_config = {
        "env_prefix": "LIVECOINWATCH_",
    }

    @field_validator("emails", mode="before")
    def validate_emails(cls, value: Dict[str, str]) -> Dict[str, str]:
        """Validate the structure of the emails dictionary."""
        for key, email in value.items():
            if not isinstance(email, str):
                raise ValueError(f"Email for {key} must be a valid string.")
        return value

    @field_validator("usernames", mode="before")
    def validate_usernames(cls, value: Dict[str, str]) -> Dict[str, str]:
        """Validate the structure of the usernames dictionary."""
        for key, username in value.items():
            if not isinstance(username, str):
                raise ValueError(f"Username for {key} must be a valid string.")
        return value
