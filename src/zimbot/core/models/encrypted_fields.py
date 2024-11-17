# src/zimbot/core/models/encrypted_fields.py

import base64
import os
from typing import Any, Optional, Type, cast

from cryptography.fernet import Fernet
from sqlalchemy.types import VARCHAR, TypeDecorator, TypeEngine

# Secure key management
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable not set.")

fernet = Fernet(ENCRYPTION_KEY.encode())


class EncryptedString(TypeDecorator):
    """
    Encrypts and decrypts string data transparently using Fernet encryption
    and base64 for encoding.
    """

    impl: Type[TypeEngine[Any]] = VARCHAR  # Correct type hint as Type[TypeEngine[Any]]
    cache_ok = True  # Indicates the type is safe to cache

    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Encrypt the value before storing it in the database.

        Args:
            value (Optional[str]): The string value to encrypt.
            dialect: The database dialect.

        Returns:
            Optional[str]: The encrypted and encoded string.
        """
        if value is None:
            return value
        # Encrypt the value
        encrypted_value = fernet.encrypt(value.encode())
        # Encode the encrypted bytes using base64
        encoded_value = base64.urlsafe_b64encode(encrypted_value).decode()
        return encoded_value

    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Decrypt the value after retrieving it from the database.

        Args:
            value (Optional[str]): The encrypted and encoded string from the database.
            dialect: The database dialect.

        Returns:
            Optional[str]: The decrypted original string.
        """
        if value is None:
            return value
        # Decode the value using base64
        encrypted_value = base64.urlsafe_b64decode(value.encode())
        # Decrypt the bytes to get the original string
        decrypted_value = fernet.decrypt(encrypted_value).decode()
        return decrypted_value

    def copy(self, **kwargs):
        """
        Create a copy of the EncryptedString type with the same length.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            EncryptedString: A new instance of EncryptedString with the same length.
        """
        # Cast self.impl to VARCHAR to access the 'length' attribute safely
        impl_cast = cast(VARCHAR, self.impl)
        return EncryptedString(impl_cast.length, **kwargs)
