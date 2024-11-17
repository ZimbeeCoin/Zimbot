# src/core/secrets/key_derivation.py

import base64
import logging
import os
from datetime import datetime
from typing import Any, Dict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


def derive_key(passphrase: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """
    Derives a secure key from a passphrase using PBKDF2HMAC.

    Args:
        passphrase (str): The passphrase to derive the key from.
        salt (bytes): A cryptographic salt to add entropy.
        iterations (int): Number of PBKDF2 iterations. Optional; default is 100,000.

    Returns:
        bytes: The derived key encoded in base64 for compatibility.

    Raises:
        Exception: If key derivation fails.
    """
    logger.debug("Deriving key from passphrase.")
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Required key length
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        logger.debug("Key derivation successful.")
        return derived_key
    except Exception as e:
        logger.error(f"Error during key derivation: {e}")
        raise


def generate_salt(length: int = 16) -> bytes:
    """
    Generates a cryptographically secure random salt.

    Args:
        length (int): The length of the salt in bytes. Optional; default is 16.

    Returns:
        bytes: The generated salt.

    Raises:
        Exception: If salt generation fails.
    """
    logger.debug(f"Generating a new salt of length {length} bytes.")
    try:
        salt = os.urandom(length)
        logger.debug("Salt generation successful.")
        return salt
    except Exception as e:
        logger.error(f"Error during salt generation: {e}")
        raise


def create_key_info(passphrase: str) -> Dict[str, Any]:
    """
    Creates key metadata with a derived key and unique salt.

    Args:
        passphrase (str): The passphrase to derive the key from.

    Returns:
        Dict[str, Any]: A dictionary containing the derived key, salt, and creation time.

    Raises:
        Exception: If key info creation fails.
    """
    logger.debug("Creating key info with unique salt.")
    try:
        salt = generate_salt()
        derived_key = derive_key(passphrase, salt)
        key_info = {
            "key": derived_key,
            "salt": salt,
            "added": datetime.utcnow(),
            # "passphrase": passphrase,  # Removed for security reasons
        }
        logger.debug("Key info creation successful.")
        return key_info
    except Exception as e:
        logger.error(f"Error during key info creation: {e}")
        raise
