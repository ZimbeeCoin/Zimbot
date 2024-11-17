from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel


class BaseConfig(BaseModel):
    """Base configuration class to set common Pydantic V2 settings."""

    model_config = {
        "extra": "allow",              # Allow additional fields not explicitly defined
        "validate_assignment": True,    # Validate fields when they are assigned
        "populate_by_name": True,      # Allow aliases to populate fields
        "frozen": False,               # Allow modification after creation
    }

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump method to include all values."""
        kwargs.setdefault("by_alias", True)        # Include aliases in the dump
        kwargs.setdefault("exclude_none", False)   # Include None values
        kwargs.setdefault("exclude_unset", False)  # Include unset values
        kwargs.setdefault("include", None)         # Include specific fields if needed
        return super().model_dump(*args, **kwargs)


T = TypeVar('T', bound='EnvConfig')


class EnvConfig(BaseModel):
    """Configuration class with environment variable support."""

    model_config = {
        "extra": "allow",                  # Allow fields not explicitly defined
        "validate_assignment": True,        # Validate fields when they are assigned
        "populate_by_name": True,          # Allow aliases to populate fields
        "use_enum_values": True,           # Use enum values instead of enum objects
        "from_attributes": True,           # Allow loading from objects with attributes
        "frozen": False,                   # Allow modification after creation
    }

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump method to include all values."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", False)
        kwargs.setdefault("exclude_unset", False)
        kwargs.setdefault("include", None)
        return super().model_dump(*args, **kwargs)

    @classmethod
    def from_env(cls: Type[T], **kwargs: Any) -> T:
        """
        Load configuration from environment variables.

        Args:
            **kwargs: Override values for configuration

        Returns:
            Instance of the configuration class
        """
        import os

        # Get all environment variables
        env_vars = {
            key.lower(): value
            for key, value in os.environ.items()
            if hasattr(cls, key.lower()) or key.lower() in kwargs
        }

        # Override with provided kwargs
        config_data = env_vars | kwargs

        return cls(**config_data)
