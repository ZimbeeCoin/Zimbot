# src/core/secrets/secrets_client.py

"""
AWS Secrets Manager client handling for synchronous and asynchronous operations.
"""

import logging
from typing import Any, Optional, Union

import aioboto3
import boto3

logger = logging.getLogger(__name__)


class AWSSecretsManagerClient:
    """
    Handles AWS Secrets Manager client initialization and operations.
    """

    def __init__(
        self,
        use_async: bool,
        region_name: str,
        boto3_client: Optional[boto3.client] = None,
        aioboto3_client: Optional[Any] = None,
    ):
        """
        Initialize the AWSSecretsManagerClient.

        Args:
            use_async (bool): Flag to determine if the client should operate asynchronously.
            region_name (str): AWS region name.
            boto3_client (Optional[boto3.client]): Injected boto3 client for synchronous operations.
            aioboto3_client (Optional[Any]): Injected aioboto3 client for asynchronous operations.
        """
        self.use_async = use_async
        self.region_name = region_name
        self.boto3_client = boto3_client
        self.aioboto3_client = aioboto3_client

        logger.debug("AWSSecretsManagerClient initialized.")

    def get_sync_client(self) -> boto3.client:
        """
        Initialize and return a synchronous Secrets Manager client.

        Returns:
            boto3.client: Synchronous AWS Secrets Manager client.
        """
        if not self.boto3_client:
            self.boto3_client = boto3.client(
                "secretsmanager", region_name=self.region_name
            )
            logger.debug("Initialized new boto3 Secrets Manager client.")
        return self.boto3_client

    async def get_async_client(self):
        """
        Initialize and return an asynchronous Secrets Manager client.

        Returns:
            aioboto3.client: Asynchronous AWS Secrets Manager client.
        """
        if not self.aioboto3_client:
            self.aioboto3_client = aioboto3.Session().client(
                "secretsmanager", region_name=self.region_name
            )
            logger.debug("Initialized new aioboto3 Secrets Manager client.")
        return self.aioboto3_client

    def get_client(self) -> Union[boto3.client, Any]:
        """
        Get AWS Secrets Manager client based on sync or async mode.

        Returns:
            Union[boto3.client, Any]: The appropriate AWS Secrets Manager client.
        """
        if self.use_async:
            if not self.aioboto3_client:
                raise RuntimeError(
                    "Async AWS client not initialized. Ensure you're using the async context manager."
                )
            return self.aioboto3_client
        else:
            return self.get_sync_client()
