# src/core/secrets/encryption_manager.py

import base64
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .circuit_breaker import with_circuit_breaker
from .encryption_service import EncryptionService
from .exceptions import DecryptionError, EncryptionError, KeyRotationError
from .key_derivation import create_key_info
from .key_storage import KeyStorageClient, StorageClientInterface
from .secrets_config import SecretsManagerConfig

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption and decryption of secrets using symmetric encryption.
    Supports key rotation, key expiry, secure key storage, backup and restore, and health checks.
    """

    def __init__(
        self,
        config: SecretsManagerConfig,
        storage_client: Optional[StorageClientInterface] = None,
        circuit_breaker: Optional[Any] = None,  # Specific circuit breaker
    ):
        """
        Initialize the EncryptionManager with a configuration and optional storage client.

        Args:
            config (SecretsManagerConfig): Configuration for the SecretsManager.
            storage_client (Optional[StorageClientInterface]): Client for secure key storage.
            circuit_breaker (Optional[Any]): Specific circuit breaker for encryption operations.
        """
        # Validate configuration
        config.validate()

        self._lock = threading.RLock()  # Reentrant lock for thread-safe operations
        self.config = config
        self.storage_client = storage_client or KeyStorageClient()
        self.circuit_breaker = circuit_breaker
        self.logger = logger

        # Initialize keys
        self.keys: List[Dict[str, Any]] = []
        initial_key_info = create_key_info(config.encryption_key)
        self.keys.append(initial_key_info)
        logger.debug("EncryptionManager initialized with the primary key.")

        # Initialize EncryptionService
        self.encryption_service = EncryptionService(self.keys)

        # Start background scheduler for periodic key expiry enforcement
        if self.config.expiry_days is not None:
            self._schedule_key_pruning()

    def _schedule_key_pruning(self):
        """Schedule periodic key pruning based on rotation_interval."""

        def prune_keys():
            while not getattr(self, "_expiry_thread_stop_event", False):
                time.sleep(self.config.rotation_interval)
                with self._lock:
                    self._enforce_key_limits()
                    if self.config.auto_key_rotation:
                        self._auto_rotate_keys_batch()

        self._expiry_thread_stop_event = False
        self._expiry_thread = threading.Thread(target=prune_keys, daemon=True)
        self._expiry_thread.start()
        logger.debug("Background key pruning scheduler started.")

    def _auto_rotate_keys_batch(self):
        """Automatically rotate multiple keys if needed."""
        if not self.config.expiry_days:
            return

        with self._lock:
            current_time = datetime.utcnow()
            approaching_expiry_keys = [
                key_info
                for key_info in self.keys
                if current_time - key_info["added"]
                > timedelta(days=self.config.expiry_days * 0.8)
            ]
            if approaching_expiry_keys:
                # Determine batch size based on number of keys nearing expiry
                batch_size = len(approaching_expiry_keys)
                logger.info(
                    f"{batch_size} key(s) nearing expiry; rotating keys automatically in batch."
                )
                try:
                    new_passphrases = [
                        Fernet.generate_key().decode() for _ in range(batch_size)
                    ]
                    self.rotate_keys(new_passphrases=new_passphrases)
                except KeyRotationError:
                    logger.error("Automatic key rotation failed.")
                    # Notify administrators via Sentry
                    try:
                        import sentry_sdk

                        sentry_sdk.capture_message(
                            "Automatic key rotation failed.", level="error"
                        )
                    except ImportError:
                        logger.warning(
                            "Sentry SDK not found. Unable to send error message."
                        )

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(KeyRotationError),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts plaintext using the EncryptionService.

        Args:
            plaintext (str): The plaintext to encrypt.

        Returns:
            str: The encrypted ciphertext.

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            return self.encryption_service.encrypt(plaintext)
        except Exception:
            logger.error("Encryption failed.", exc_info=False)
            raise EncryptionError("Encryption failed.")

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(DecryptionError),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def decrypt(self, ciphertext: str, reencrypt: bool = False) -> str:
        """
        Decrypts ciphertext using the EncryptionService.

        Args:
            ciphertext (str): The ciphertext to decrypt.
            reencrypt (bool): If True, re-encrypts with the primary key if decrypted with an old key.

        Returns:
            str: The decrypted plaintext.

        Raises:
            DecryptionError: If decryption fails with all keys.
        """
        try:
            return self.encryption_service.decrypt(ciphertext, reencrypt)
        except Exception:
            logger.error("Decryption failed.", exc_info=False)
            raise DecryptionError("Decryption failed.")

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(KeyRotationError),
        reraise=True,
    )
    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def rotate_keys(
        self,
        new_passphrases: List[str],
    ):
        """
        Rotate encryption keys by adding new primary keys with retry logic.

        Args:
            new_passphrases (List[str]): List of new passphrases to derive encryption keys.

        Raises:
            KeyRotationError: If key rotation fails after retries.
        """
        try:
            with self._lock:
                new_key_infos = [
                    create_key_info(passphrase) for passphrase in new_passphrases
                ]
                self.keys = (
                    new_key_infos + self.keys
                )  # Batch add new keys at the beginning
            self._enforce_key_limits()
            self.encryption_service.update_keys(self.keys)
            logger.info("Encryption keys rotated successfully in batch.")

            # Audit log for key rotation
            logger.info("AUDIT: Performed batch key rotation.")

            # Save updated keys to secure storage if available
            self.save_keys_to_secure_storage(
                retention_limit=self.config.backup_retention_limit
            )

        except Exception:
            logger.error("Batch key rotation failed.", exc_info=False)
            raise KeyRotationError(
                "Failed to rotate encryption keys after multiple attempts."
            )

    def _enforce_key_limits(self):
        """Enforce maximum key count and remove expired keys."""
        current_time = datetime.utcnow()

        # Remove expired keys
        if self.config.expiry_days is not None:
            expiry_threshold = current_time - timedelta(days=self.config.expiry_days)
            original_count = len(self.keys)
            self.keys = [
                key_info
                for key_info in self.keys
                if key_info["added"] > expiry_threshold
            ]
            expired_count = original_count - len(self.keys)
            if expired_count > 0:
                logger.info(f"Removed {expired_count} expired encryption key(s).")
                # Audit log for key removal
                logger.info(
                    f"AUDIT: Removed {expired_count} expired encryption key(s)."
                )

        # Enforce maximum key limit
        if self.config.max_keys is not None and len(self.keys) > self.config.max_keys:
            removed_keys = self.keys[self.config.max_keys :]
            self.keys = self.keys[: self.config.max_keys]
            logger.info(
                f"Removed {len(removed_keys)} key(s) to enforce max_keys limit."
            )
            # Audit log for key removal
            logger.info(
                f"AUDIT: Removed {len(removed_keys)} key(s) to enforce max_keys limit."
            )

    def remove_old_key(self, key_index: int):
        """
        Remove an old encryption key by its index.

        Args:
            key_index (int): The index of the key to remove.

        Raises:
            IndexError: If the key_index is out of range.
        """
        try:
            with self._lock:
                self.keys.pop(key_index)
                self.encryption_service.update_keys(self.keys)
                logger.info(f"Removed old encryption key at index {key_index}.")

                # Audit log for key removal
                logger.info(f"AUDIT: Removed old encryption key at index {key_index}.")

                # Save updated keys to secure storage if available
                self.save_keys_to_secure_storage(
                    retention_limit=self.config.backup_retention_limit
                )
        except IndexError:
            logger.error(f"Failed to remove key at index {key_index}.")
            raise

    def get_active_keys_metadata(self) -> List[Dict[str, Any]]:
        """
        Get a list of currently active encryption keys with their metadata.

        Returns:
            List[Dict[str, Any]]: List of active keys with metadata.
        """
        with self._lock:
            return [
                {
                    "added": key_info["added"].isoformat(),
                }
                for key_info in self.keys
            ]

    def backup_keys(self, retention_limit: Optional[int] = None):
        """
        Backup current encryption keys using the storage client with a retention policy.

        Args:
            retention_limit (Optional[int]): Maximum number of backups to retain.
                                             If None, no limit is enforced.

        Raises:
            Exception: If backup fails.
        """
        try:
            keys_data = self._get_keys_data_for_backup()
            self.storage_client.backup_keys(keys_data, retention_limit=retention_limit)
            logger.info("Encryption keys backed up successfully.")

            # Audit log for backup
            logger.info("AUDIT: Performed key backup.")
        except Exception:
            logger.error("Failed to backup keys.", exc_info=False)
            raise

    def _get_keys_data_for_backup(self) -> List[Dict[str, Any]]:
        """Prepare keys data for backup, including masking sensitive information."""
        with self._lock:
            return [
                {
                    "key": base64.urlsafe_b64encode(key_info["key"]).decode(),
                    "salt": base64.urlsafe_b64encode(key_info["salt"]).decode(),
                    "added": key_info["added"].isoformat(),
                }
                for key_info in self.keys
            ]

    def restore_keys(self):
        """
        Restore encryption keys from backup using the storage client.

        Raises:
            Exception: If restoration fails.
        """
        try:
            keys_data = self.storage_client.restore_keys()
            with self._lock:
                self.keys = []
                for key_record in keys_data:
                    key_info = {
                        "key": base64.urlsafe_b64decode(key_record["key"].encode()),
                        "salt": base64.urlsafe_b64decode(key_record["salt"].encode()),
                        "added": datetime.fromisoformat(key_record["added"]),
                    }
                    self.keys.append(key_info)
                self.encryption_service.update_keys(self.keys)
            logger.info("Encryption keys restored from backup successfully.")

            # Audit log for restoration
            logger.info("AUDIT: Restored encryption keys from backup.")
        except Exception:
            logger.error("Failed to restore keys.", exc_info=False)
            raise

    def load_keys_from_secure_storage(self):
        """
        Load encryption keys from the secure storage client.

        Raises:
            Exception: If keys cannot be loaded.
        """
        try:
            keys_data = self.storage_client.retrieve_keys()
            with self._lock:
                self.keys = []
                for key_record in keys_data:
                    key_info = {
                        "key": base64.urlsafe_b64decode(key_record["key"].encode()),
                        "salt": base64.urlsafe_b64decode(key_record["salt"].encode()),
                        "added": datetime.fromisoformat(key_record["added"]),
                    }
                    self.keys.append(key_info)
                self.encryption_service.update_keys(self.keys)
            logger.info("Encryption keys loaded from secure storage.")

            # Audit log for loading keys
            logger.info("AUDIT: Loaded encryption keys from secure storage.")
        except Exception:
            logger.error("Failed to load keys from secure storage.", exc_info=False)
            raise

    def save_keys_to_secure_storage(self, retention_limit: Optional[int] = None):
        """
        Save current encryption keys to the secure storage client with a retention policy.

        Args:
            retention_limit (Optional[int]): Maximum number of backups to retain.
                                             If None, no limit is enforced.

        Raises:
            Exception: If keys cannot be saved.
        """
        try:
            keys_data = self._get_keys_data_for_backup()
            self.storage_client.store_keys(keys_data)
            logger.info("Encryption keys saved to secure storage.")

            # Audit log for saving keys
            logger.info("AUDIT: Saved encryption keys to secure storage.")

            # Perform backup with retention policy
            self.backup_keys(retention_limit=retention_limit)
        except Exception:
            logger.error("Failed to save keys to secure storage.", exc_info=False)
            raise

    def shutdown(self):
        """
        Gracefully shut down the EncryptionManager, stopping the background scheduler.
        """
        if hasattr(self, "_expiry_thread_stop_event"):
            logger.info("Shutting down EncryptionManager's background scheduler.")
            self._expiry_thread_stop_event = True
            self._expiry_thread.join(timeout=5)
            logger.info("EncryptionManager shut down successfully.")

            # Audit log for shutdown
            logger.info("AUDIT: EncryptionManager shutdown completed.")

    def health_check(self) -> bool:
        """
        Perform a health check by encrypting and decrypting a test message.

        Returns:
            bool: True if encryption and decryption are successful, False otherwise.
        """
        test_message = "encryption_health_check"
        try:
            encrypted = self.encrypt(test_message)
            decrypted = self.decrypt(encrypted)
            if decrypted == test_message:
                logger.debug("EncryptionManager health check passed.")
                return True
            else:
                logger.error(
                    "EncryptionManager health check failed: Mismatch in decrypted message."
                )
                return False
        except Exception:
            logger.error("EncryptionManager health check failed.", exc_info=False)
            return False
