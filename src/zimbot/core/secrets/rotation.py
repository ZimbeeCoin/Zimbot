# src/core/secrets/rotation.py

"""
Module for managing periodic rotation of secrets.
"""

import asyncio
import logging
from typing import List, Optional

import sentry_sdk

from .alerting import Alerting

logger = logging.getLogger(__name__)


class SecretsRotator:
    """
    Manages periodic rotation of secrets.
    """

    def __init__(
        self,
        secrets_retriever: Any,  # Reference to SecretsRetriever
        encryption_manager: Any,  # Reference to EncryptionManager
        secret_names: Optional[List[str]] = None,
        interval: int = 86400,  # Default to 24 hours
        alerting: Optional[Alerting] = None,
    ):
        """
        Initialize the SecretsRotator.

        Args:
            secrets_retriever (Any): Instance of SecretsRetriever to refresh secrets.
            encryption_manager (Any): Instance of EncryptionManager to rotate keys.
            secret_names (Optional[List[str]]): List of secrets to rotate. If None, rotate all.
            interval (int): Interval in seconds between rotations.
            alerting (Optional[Alerting]): Alerting utility for sending alerts.
        """
        self.secrets_retriever = secrets_retriever
        self.encryption_manager = encryption_manager
        self.secret_names = secret_names or []
        self.interval = interval
        self.alerting = alerting
        self.task: Optional[asyncio.Task] = None

    @with_circuit_breaker(
        lambda self: self.circuit_breaker_manager.get_encryption_circuit_breaker()
    )
    async def rotate_secrets_periodically(self):
        """
        Periodically rotate secrets based on the specified interval.
        """
        logger.debug("Starting periodic secrets rotation task.")
        while True:
            try:
                if self.secret_names:
                    refreshed = await self.secrets_retriever.refresh_all_secrets_async(
                        self.secret_names
                    )
                    logger.info(f"Successfully rotated secrets: {refreshed}")
                else:
                    logger.warning("No secret names provided for rotation.")
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                logger.info("Secrets rotation task has been cancelled.")
                break
            except Exception as e:
                logger.error(f"Error during secrets rotation: {e}")
                sentry_sdk.capture_exception(e)
                if self.alerting:
                    await self.alerting.send_alert(
                        f"Error during secrets rotation: {e}"
                    )
                await asyncio.sleep(self.interval)  # Wait before retrying

    def start_rotation(self):
        """
        Start the secrets rotation task.
        """
        if not self.task:
            self.task = asyncio.create_task(self.rotate_secrets_periodically())
            logger.info("Secrets rotation task started.")

    def stop_rotation(self):
        """
        Stop the secrets rotation task.
        """
        if self.task:
            self.task.cancel()
            logger.info("Secrets rotation task stopped.")
            self.task = None
