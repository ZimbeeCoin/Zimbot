# src/core/secrets/health_check.py

"""
Module for performing health checks on SecretsManager components.
"""

import asyncio
import logging
from typing import Optional

from .alerting import Alerting
from .aws_client_manager import AWSSecretsClientManager
from .circuit_breaker import CircuitBreakerManager
from .encryption_manager import EncryptionManager
from .redis_client_manager import RedisClientManager

logger = logging.getLogger(__name__)


class SecretsManagerHealthCheck:
    """
    Performs health checks to ensure SecretsManager components are operational.
    """

    def __init__(
        self,
        aws_client_manager: AWSSecretsClientManager,
        redis_client_manager: RedisClientManager,
        circuit_breaker_manager: CircuitBreakerManager,
        alerting: Optional[Alerting] = None,
        encryption_manager: Optional[EncryptionManager] = None,
    ):
        """
        Initialize the SecretsManagerHealthCheck.

        Args:
            aws_client_manager (AWSSecretsClientManager): AWS client manager instance.
            redis_client_manager (RedisClientManager): Redis client manager instance.
            circuit_breaker_manager (CircuitBreakerManager): Circuit breaker manager instance.
            alerting (Optional[Alerting]): Alerting utility instance.
            encryption_manager (Optional[EncryptionManager]): Encryption manager instance.
        """
        self.aws_client_manager = aws_client_manager
        self.redis_client_manager = redis_client_manager
        self.circuit_breaker_manager = circuit_breaker_manager
        self.alerting = alerting
        self.encryption_manager = encryption_manager

    async def perform_health_check(self) -> bool:
        """
        Perform a comprehensive health check.

        Returns:
            bool: True if all components are healthy, False otherwise.
        """
        logger.info("Starting SecretsManager health check.")
        health_checks = [
            self._check_aws_secrets_manager(),
            self._check_redis(),
            self._check_circuit_breakers(),
            self._check_alerting(),
            self._check_encryption_manager(),
        ]
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        all_healthy = all(result is True for result in results)

        if not all_healthy:
            failed_checks = [str(check) for check in results if check is not True]
            error_message = f"SecretsManager health check failed for components: {', '.join(failed_checks)}"
            logger.error(error_message)
            if self.alerting:
                await self.alerting.send_alert(error_message)
            return False

        logger.info("SecretsManager health check passed.")
        return True

    async def _check_aws_secrets_manager(self) -> bool:
        """Check AWS Secrets Manager connectivity."""
        try:
            if self.aws_client_manager.use_async:
                async_client = await self.aws_client_manager.get_async_client()
                await async_client.list_secrets(MaxResults=1)
            else:
                sync_client = self.aws_client_manager.get_sync_client()
                sync_client.list_secrets(MaxResults=1)
            logger.debug("AWS Secrets Manager connectivity: Healthy.")
            return True
        except Exception as e:
            logger.error("AWS Secrets Manager health check failed.", exc_info=True)
            return False

    async def _check_redis(self) -> bool:
        """Check Redis connectivity."""
        try:
            if self.redis_client_manager.use_async:
                async_client = await self.redis_client_manager.create_async_redis_pool()
                await async_client.ping()
                await async_client.close()
            else:
                sync_client = self.redis_client_manager.create_sync_redis_client()
                sync_client.ping()
                sync_client.close()
            logger.debug("Redis connectivity: Healthy.")
            return True
        except Exception as e:
            logger.error("Redis health check failed.", exc_info=True)
            return False

    async def _check_circuit_breakers(self) -> bool:
        """Check the state of circuit breakers."""
        try:
            unhealthy_breakers = []
            for name in self.circuit_breaker_manager.get_circuit_breaker_names():
                breaker = self.circuit_breaker_manager.get_circuit_breaker(name)
                if breaker.is_open():
                    unhealthy_breakers.append(name)
            if unhealthy_breakers:
                logger.warning(
                    f"Circuit breakers open: {', '.join(unhealthy_breakers)}"
                )
                return False
            logger.debug("All circuit breakers are closed and healthy.")
            return True
        except Exception as e:
            logger.error("Circuit breaker health check failed.", exc_info=True)
            return False

    async def _check_alerting(self) -> bool:
        """Check alerting system availability."""
        if not self.alerting:
            logger.warning("Alerting system is not configured.")
            return True  # Not critical if alerting is not set up

        test_message = "Health check: Alerting system test."
        try:
            await self.alerting.send_alert(test_message)
            logger.debug("Alerting system is operational.")
            return True
        except Exception as e:
            logger.error("Alerting system health check failed.", exc_info=True)
            return False

    async def _check_encryption_manager(self) -> bool:
        """Check encryption manager health."""
        if not self.encryption_manager:
            logger.warning("EncryptionManager is not configured.")
            return True  # Not critical if encryption manager is not set up

        try:
            is_healthy = self.encryption_manager.health_check()
            if is_healthy:
                logger.debug("EncryptionManager is healthy.")
                return True
            else:
                logger.error("EncryptionManager health check failed.")
                return False
        except Exception as e:
            logger.error(
                "EncryptionManager health check raised an exception.", exc_info=True
            )
            return False
