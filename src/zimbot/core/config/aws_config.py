from typing import Optional

from pydantic import BaseModel, Field, SecretStr


class AWSSettings(BaseModel):
    """Centralized AWS configuration settings."""

    region: str = Field(
        default="us-west-1",
        description="AWS region for resource deployment."
    )
    access_key_id: Optional[SecretStr] = Field(
        default=None,
        description="AWS access key ID for API access."
    )
    secret_access_key: Optional[SecretStr] = Field(
        default=None,
        description="AWS secret access key for API access."
    )
    session_token: Optional[SecretStr] = Field(
        default=None,
        description="AWS session token for temporary credentials."
    )
    use_secrets_manager: bool = Field(
        default=False,
        description=(
            "Toggle to use AWS Secrets Manager for secrets management."
        )
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"
        validate_assignment = True

    def is_aws_enabled(self) -> bool:
        """Helper method to check if AWS Secrets Manager is enabled."""
        return self.use_secrets_manager

    def refresh_settings(self):
        """
        Refresh settings by re-reading environment variables.
        Useful if environment variables might change at runtime.
        """
        updated_values = self.model_dump(exclude_unset=True)
        # Validate the updated values
        updated = self.model_validate(updated_values)
        # Update the current instance's __dict__ with the new values
        self.__dict__.update(updated.__dict__)


# Instantiate AWSSettings for usage
aws_settings = AWSSettings()
print(aws_settings)
