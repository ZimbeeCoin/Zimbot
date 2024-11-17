# src/zimbot/core/secrets/key_storage.py

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Protocol, cast

logger = logging.getLogger(__name__)


class StorageClientInterface(Protocol):
    """Protocol for secure storage client."""

    def retrieve_keys(self) -> List[Dict[str, Any]]:
        """
        Retrieve keys from secure storage.
        """
        ...

    def store_keys(self, keys_data: List[Dict[str, Any]]):
        """
        Store keys to secure storage.

        Args:
            keys_data (List[Dict[str, Any]]): A list of key metadata dictionaries.
        """
        ...

    def backup_keys(
        self, keys_data: List[Dict[str, Any]], retention_limit: Optional[int] = None
    ):
        """
        Backup keys with an optional retention policy.

        Args:
            keys_data (List[Dict[str, Any]]): A list of key metadata dictionaries.
            retention_limit (Optional[int]): Maximum number of backups to retain.
                If None, no limit is enforced.
        """
        ...

    def restore_keys(self) -> List[Dict[str, Any]]:
        """
        Restore keys from backup.
        """
        ...


class KeyStorageClient(StorageClientInterface):
    """Concrete implementation of StorageClientInterface."""

    def __init__(
        self,
        storage_path: str = "keys.json",
        backup_dir: str = "key_backups",
        expiry_days: Optional[int] = None,
    ):
        """
        Initialize the KeyStorageClient with storage paths.

        Args:
            storage_path (str): Path to the main key storage file.
            backup_dir (str): Directory where backups are stored.
            expiry_days (Optional[int]): Number of days after which keys expire.
        """
        self.storage_path = storage_path
        self.backup_dir = backup_dir
        self.expiry_days = expiry_days
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.debug(
            f"KeyStorageClient initialized with storage_path={self.storage_path}, "
            f"backup_dir={self.backup_dir}, expiry_days={self.expiry_days}."
        )

    def retrieve_keys(self) -> List[Dict[str, Any]]:
        """
        Retrieve keys from secure storage, removing expired keys.

        Returns:
            List[Dict[str, Any]]: List of key metadata dictionaries.

        Raises:
            Exception: If retrieval fails.
        """
        logger.debug("Retrieving keys from secure storage.")
        try:
            with open(self.storage_path) as file:
                keys_data = json.load(file)
            logger.debug("Keys retrieved successfully.")

            # Remove expired keys
            if self.expiry_days is not None:
                keys_data = self._remove_expired_keys(keys_data)
            return keys_data
        except FileNotFoundError:
            logger.warning("No keys found in secure storage.")
            return []
        except Exception as retrieval_error:
            logger.error(f"Error retrieving keys: {retrieval_error}", exc_info=True)
            raise

    def store_keys(self, keys_data: List[Dict[str, Any]]):
        """
        Store keys to secure storage, removing expired keys.

        Args:
            keys_data (List[Dict[str, Any]]): List of key metadata dictionaries.

        Raises:
            Exception: If storing keys fails.
        """
        logger.debug("Storing keys to secure storage.")
        try:
            # Remove expired keys before storing
            if self.expiry_days is not None:
                keys_data = self._remove_expired_keys(keys_data)

            self._save_keys_to_storage(keys_data)
        except Exception as storage_error:
            logger.error(f"Error storing keys: {storage_error}", exc_info=True)
            raise

    def _remove_expired_keys(
        self, keys_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove expired keys based on the expiry_days setting.

        Args:
            keys_data (List[Dict[str, Any]]): List of key metadata dictionaries.

        Returns:
            List[Dict[str, Any]]: Filtered list of key metadata dictionaries.
        """
        current_time = datetime.utcnow()
        if self.expiry_days is not None:
            expiry_threshold = current_time - timedelta(
                days=cast(int, self.expiry_days)
            )
        else:
            expiry_threshold = current_time
        original_count = len(keys_data)
        filtered_keys = [
            key_info
            for key_info in keys_data
            if datetime.fromisoformat(key_info["added"]) > expiry_threshold
        ]
        expired_count = original_count - len(filtered_keys)
        if expired_count > 0:
            logger.info(f"Removed {expired_count} expired key(s) from storage.")
            # Audit log for key removal
            logger.info(f"AUDIT: Removed {expired_count} expired key(s) from storage.")
            # Save updated keys back to storage
            self._save_keys_to_storage(filtered_keys)
        return filtered_keys

    def _save_keys_to_storage(self, keys_data: List[Dict[str, Any]]):
        """
        Save keys to storage file.

        Args:
            keys_data (List[Dict[str, Any]]): List of key metadata dictionaries.

        Raises:
            Exception: If storing keys fails.
        """
        try:
            with open(self.storage_path, "w") as file:
                json.dump(keys_data, file, default=str, indent=4)
            logger.debug("Keys stored successfully.")

            # Audit log for storing keys
            logger.info("AUDIT: Stored encryption keys to secure storage.")
        except Exception as save_error:
            logger.error(f"Error saving keys to storage: {save_error}", exc_info=True)
            raise

    def backup_keys(
        self, keys_data: List[Dict[str, Any]], retention_limit: Optional[int] = None
    ):
        """
        Backup keys with an optional retention policy.

        Args:
            keys_data (List[Dict[str, Any]]): List of key metadata dictionaries.
            retention_limit (Optional[int]): Maximum number of backups to retain.
                If None, no limit is enforced.

        Raises:
            Exception: If backup fails.
        """
        logger.debug("Backing up keys.")
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            backup_filename = os.path.join(
                self.backup_dir, f"keys_backup_{timestamp}.json"
            )
            with open(backup_filename, "w") as file:
                json.dump(keys_data, file, default=str, indent=4)
            logger.debug(f"Keys backed up successfully to {backup_filename}.")

            # Audit log for backup
            logger.info(f"AUDIT: Performed key backup to {backup_filename}.")

            if retention_limit is not None:
                self._enforce_backup_retention_limit(retention_limit)
        except Exception as backup_error:
            logger.error(f"Error during key backup: {backup_error}", exc_info=True)
            raise

    def _enforce_backup_retention_limit(self, retention_limit: int):
        """
        Enforce the backup retention policy by removing old backups.

        Args:
            retention_limit (int): Maximum number of backups to retain.

        Raises:
            Exception: If backup retention enforcement fails.
        """
        backups = sorted(
            [f for f in os.listdir(self.backup_dir) if f.startswith("keys_backup_")],
            reverse=True,
        )
        for backup in backups[retention_limit:]:
            backup_path = os.path.join(self.backup_dir, backup)
            try:
                os.remove(backup_path)
                logger.debug(
                    f"Old backup {backup_path} removed to enforce retention limit."
                )

                # Audit log for backup removal
                logger.info(
                    f"AUDIT: Removed old backup {backup_path} to enforce retention limit."
                )
            except Exception as removal_error:
                logger.error(
                    f"Error removing old backup {backup_path}: {removal_error}",
                    exc_info=True,
                )
                raise

    def restore_keys(self) -> List[Dict[str, Any]]:
        """
        Restore keys from the latest backup.

        Returns:
            List[Dict[str, Any]]: List of key metadata dictionaries.

        Raises:
            Exception: If restoration fails.
        """
        logger.debug("Restoring keys from backup.")
        try:
            backups = sorted(
                [
                    f
                    for f in os.listdir(self.backup_dir)
                    if f.startswith("keys_backup_")
                ],
                reverse=True,
            )
            if not backups:
                logger.warning("No backup files found.")
                return []
            latest_backup = backups[0]
            backup_path = os.path.join(self.backup_dir, latest_backup)
            with open(backup_path) as file:
                keys_data = json.load(file)
            logger.debug(f"Keys restored successfully from {backup_path}.")

            # Audit log for restoration
            logger.info(f"AUDIT: Restored encryption keys from backup {backup_path}.")

            # Remove expired keys after restoration
            if self.expiry_days is not None:
                keys_data = self._remove_expired_keys(keys_data)

            return keys_data
        except Exception as restoration_error:
            logger.error(
                f"Error restoring keys from backup: {restoration_error}", exc_info=True
            )
            raise
