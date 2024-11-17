# src/core/secrets/encryption_service.py

import logging
import threading
from typing import Any, Dict, List

from cryptography.fernet import Fernet, InvalidToken

from .exceptions import DecryptionError, EncryptionError

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Handles encryption and decryption using derived keys.
    Maintains a list of Fernet instances for encryption and decryption of secrets.
    """

    def __init__(self, keys_info: List[Dict[str, Any]]):
        """
        Initialize the EncryptionService with a list of key information dictionaries.

        Args:
            keys_info (List[Dict[str, Any]]): List of key metadata dictionaries.
        """
        self._lock = threading.RLock()
        self.fernets: List[Fernet] = []
        self.update_keys(keys_info)

    def update_keys(self, keys_info: List[Dict[str, Any]]):
        """
        Update the list of Fernet instances based on current keys.

        Args:
            keys_info (List[Dict[str, Any]]): Updated list of key metadata dictionaries.
        """
        with self._lock:
            self.fernets = [Fernet(key_info["key"]) for key_info in keys_info]
            logger.debug(f"Updated Fernet instances. Total keys: {len(self.fernets)}")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts plaintext with the primary (most recent) key.

        Args:
            plaintext (str): The plaintext to encrypt.

        Returns:
            str: The encrypted ciphertext as a URL-safe base64-encoded string.

        Raises:
            EncryptionError: If encryption fails.
        """
        with self._lock:
            if not self.fernets:
                logger.error("No encryption keys available for encryption.")
                raise EncryptionError("No encryption keys available.")
            primary_fernet = self.fernets[0]
        try:
            ciphertext = primary_fernet.encrypt(plaintext.encode()).decode()
            logger.debug("Encryption successful.")
            return ciphertext
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError("Encryption failed.") from e

    def decrypt(self, ciphertext: str, reencrypt: bool = False) -> str:
        """
        Attempts to decrypt ciphertext with available keys.

        Args:
            ciphertext (str): The ciphertext to decrypt.
            reencrypt (bool): If True, re-encrypts the plaintext with the primary key if decryption succeeds with an old key.

        Returns:
            str: The decrypted plaintext.

        Raises:
            DecryptionError: If decryption fails with all keys.
        """
        with self._lock:
            fernets_copy = list(self.fernets)  # Copy to prevent race conditions

        for index, fernet in enumerate(fernets_copy):
            try:
                plaintext = fernet.decrypt(ciphertext.encode(), ttl=None).decode()
                logger.debug(f"Decryption successful using key at index {index}.")

                # Re-encrypt with primary key if decrypted with old key
                if reencrypt and index != 0:
                    logger.debug("Re-encrypting data with the primary key.")
                    return self.encrypt(plaintext)
                return plaintext

            except InvalidToken:
                logger.debug(
                    f"InvalidToken with key at index {index}. Trying next key."
                )
                continue
            except Exception as e:
                logger.error(f"Decryption error with key at index {index}: {e}")
                continue

        logger.error("Decryption failed with all available keys.")
        raise DecryptionError("Failed to decrypt with all available keys.")
