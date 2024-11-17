from typing import Any, Dict, Optional

from pydantic import AnyHttpUrl, Field, field_validator

from .base import BaseConfig


class LiveKitSettings(BaseConfig):
    """Settings for LiveKit integration."""

    name: Optional[str] = Field(
        default="ZimbotLiveKit",
        description="Name for LiveKit, e.g., 'ZimbotLiveKit'."
    )
    websocket_url: AnyHttpUrl = Field(
        ...,
        description="WebSocket URL for LiveKit, e.g., 'wss://livekit.example.com'."
    )
    sip_uri: Optional[str] = Field(
        default=None,
        description="SIP URI for LiveKit, e.g., 'sip:zimbot@example.com'."
    )
    default_room_name: Optional[str] = Field(
        default="default_room",
        description="Default room name if applicable."
    )
    participant_roles: Dict[str, str] = Field(
        default_factory=lambda: {"host": "publish", "guest": "subscribe"},
        description="Roles for participants, e.g., host, guest."
    )
    ws_timeout: int = Field(
        default=30,
        ge=5,
        description="Timeout in seconds for WebSocket connections."
    )
    ws_reconnect_attempts: int = Field(
        default=3,
        ge=0,
        description="Number of reconnection attempts for WebSocket."
    )
    recording_enabled: bool = Field(
        default=False,
        description="Enable or disable recording for LiveKit sessions."
    )
    recording_options: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"format": "mp4", "resolution": "720p"},
        description="Recording options for LiveKit, if applicable."
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for LiveKit."
    )

    model_config = {
        "env_prefix": "LIVEKIT_",
    }

    @field_validator("sip_uri")
    def validate_sip_uri(cls, value: Optional[str]) -> Optional[str]:
        """Validate SIP URI if provided."""
        if value and not value.startswith("sip:"):
            raise ValueError("SIP URI must start with 'sip:'.")
        return value

    @field_validator("participant_roles")
    def validate_participant_roles(cls, roles: Dict[str, str]) -> Dict[str, str]:
        """Ensure participant roles are valid."""
        allowed_roles = {"publish", "subscribe"}
        for role, permission in roles.items():
            if permission not in allowed_roles:
                raise ValueError(
                    f"Invalid permission '{permission}' for role '{role}'."
                )
        return roles

    @field_validator("recording_options")
    def validate_recording_options(cls, options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recording options."""
        allowed_formats = {"mp4", "mkv"}
        format_ = options.get("format")
        if format_ and format_ not in allowed_formats:
            raise ValueError(
                f"Invalid recording format '{format_}'. "
                f"Allowed: {', '.join(allowed_formats)}"
            )
        return options
