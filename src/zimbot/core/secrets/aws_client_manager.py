# src/core/aws/aws_client_manager.py

import asyncio
import logging
from typing import Any, Dict, Optional, Type

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import get_aws_config  # Assuming a shared configuration module
from .alerting import Alerting  # Standardized alerting interface

# Import centralized decorators and configurations
from .circuit_breaker import with_circuit_breaker
from .error_handling import handle_error
from .exceptions import AWSClientError  # Custom exception for AWS-related errors

logger = logging.getLogger(__name__)


class AWSClientManager:
    """
    Manages AWS clients for services like S3 and DynamoDB.
    Delegates cross-cutting concerns like circuit breaking and alerting to centralized modules.
    """

    def __init__(
        self,
        use_async: bool = False,  # Placeholder for future async support
        circuit_breaker: Optional[
            Type
        ] = None,  # Replace with specific CircuitBreaker type if available
        alerting: Optional[Alerting] = None,
    ):
        """
        Initialize the AWSClientManager with minimal external logic.

        Args:
            use_async (bool): Flag to determine if the manager should operate asynchronously.
                              Currently, boto3 is synchronous. Future implementations might support async clients.
            circuit_breaker (Optional[Type]): Circuit breaker instance for AWS operations.
            alerting (Optional[Alerting]): Alerting utility for sending alerts.
        """
        config = get_aws_config()
        self.aws_config = config.get("AWS", {})
        self.use_async = use_async
        self.circuit_breaker = circuit_breaker
        self.alerting = alerting
        self._clients: Dict[str, Any] = {}  # Stores boto3 clients by service name

    def _handle_error(self, error: Exception, message: str):
        """
        Centralized error handling; delegates alerting if configured.

        Args:
            error (Exception): The exception to handle.
            message (str): The error message.
        """
        handle_error(error, message, logger, self.alerting)

    def _get_boto3_client(self, service_name: str) -> Any:
        """
        Get or create a boto3 client for the specified AWS service.

        Args:
            service_name (str): The name of the AWS service (e.g., 's3', 'dynamodb').

        Returns:
            Any: The boto3 client for the specified service.

        Raises:
            AWSClientError: If creating the client fails.
        """
        if service_name in self._clients:
            logger.debug(f"Using existing boto3 client for service: {service_name}")
            return self._clients[service_name]

        try:
            client = boto3.client(
                service_name,
                region_name=self.aws_config.get("REGION"),
                aws_access_key_id=self.aws_config.get("ACCESS_KEY_ID"),
                aws_secret_access_key=self.aws_config.get("SECRET_ACCESS_KEY"),
                aws_session_token=self.aws_config.get("SESSION_TOKEN"),
                # Additional configuration parameters can be added here
            )
            self._clients[service_name] = client
            logger.info(f"Created new boto3 client for service: {service_name}")
            return client
        except (BotoCoreError, ClientError) as e:
            self._handle_error(
                e, f"Failed to create boto3 client for service: {service_name}"
            )
            raise AWSClientError(
                f"Failed to create boto3 client for service: {service_name}"
            ) from e

    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def list_s3_buckets(self) -> Optional[Dict[str, Any]]:
        """
        List all S3 buckets in the AWS account.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing bucket information, or None if failed.

        Raises:
            AWSClientError: If the operation fails.
        """
        client = self._get_boto3_client("s3")
        try:
            response = client.list_buckets()
            logger.debug("Successfully listed S3 buckets.")
            return response
        except (BotoCoreError, ClientError) as e:
            self._handle_error(e, "Failed to list S3 buckets")
            raise AWSClientError("Failed to list S3 buckets") from e

    @with_circuit_breaker(lambda self: self.circuit_breaker)
    def get_dynamodb_table_description(
        self, table_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the description of a DynamoDB table.

        Args:
            table_name (str): The name of the DynamoDB table.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing table description, or None if failed.

        Raises:
            AWSClientError: If the operation fails.
        """
        client = self._get_boto3_client("dynamodb")
        try:
            response = client.describe_table(TableName=table_name)
            logger.debug(
                f"Successfully retrieved description for DynamoDB table: {table_name}"
            )
            return response
        except (BotoCoreError, ClientError) as e:
            self._handle_error(e, f"Failed to describe DynamoDB table: {table_name}")
            raise AWSClientError(
                f"Failed to describe DynamoDB table: {table_name}"
            ) from e

    def close_all_clients(self):
        """
        Close all boto3 clients managed by this manager.
        Note: boto3 clients do not require explicit closure, but this method can be used for cleanup if needed.
        """
        self._clients.clear()
        logger.info("All boto3 clients have been cleared.")

    # Future implementations can include async support using aiobotocore or
    # similar libraries.
