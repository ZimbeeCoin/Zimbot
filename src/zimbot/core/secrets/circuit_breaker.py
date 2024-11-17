# src/core/secrets/circuit_breaker.py

import asyncio
import logging
from functools import wraps
from typing import Callable, Optional

from pybreaker import CircuitBreaker, CircuitBreakerListener

logger = logging.getLogger(__name__)


class CircuitBreakerManager:
    """
    Manages individual circuit breakers for different components.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_time: int = 60,
        encryption_failure_threshold: int = 3,
        encryption_recovery_time: int = 120,
        alerting: Optional[Any] = None,  # Reference to Alerting utility
    ):
        """
        Initialize the CircuitBreakerManager with specific settings.

        Args:
            failure_threshold (int): Number of failures to trip the circuit.
            recovery_time (int): Time in seconds to wait before attempting to reset the circuit.
            encryption_failure_threshold (int): Specific failure threshold for encryption.
            encryption_recovery_time (int): Specific recovery time for encryption circuit breaker.
            alerting (Optional[Any]): Alerting utility for sending alerts on circuit breaker events.
        """
        self.alerting = alerting

        # Define listeners for circuit breaker events
        self.listener = CircuitBreakerListener()

        # Initialize circuit breakers
        self.aws_circuit_breaker = CircuitBreaker(
            name="AWSSecretsManager",
            fail_max=failure_threshold,
            reset_timeout=recovery_time,
            listeners=[self.listener],
        )

        self.redis_circuit_breaker = CircuitBreaker(
            name="Redis",
            fail_max=failure_threshold,
            reset_timeout=recovery_time,
            listeners=[self.listener],
        )

        self.encryption_circuit_breaker = CircuitBreaker(
            name="Encryption",
            fail_max=encryption_failure_threshold,
            reset_timeout=encryption_recovery_time,
            listeners=[self.listener],
        )

        # Attach event handlers
        self.aws_circuit_breaker.add_event_listener(
            "failure", self._circuit_failure_handler
        )
        self.aws_circuit_breaker.add_event_listener("open", self._circuit_open_handler)
        self.aws_circuit_breaker.add_event_listener(
            "half_open", self._circuit_half_open_handler
        )

        self.redis_circuit_breaker.add_event_listener(
            "failure", self._circuit_failure_handler
        )
        self.redis_circuit_breaker.add_event_listener(
            "open", self._circuit_open_handler
        )
        self.redis_circuit_breaker.add_event_listener(
            "half_open", self._circuit_half_open_handler
        )

        self.encryption_circuit_breaker.add_event_listener(
            "failure", self._circuit_failure_handler
        )
        self.encryption_circuit_breaker.add_event_listener(
            "open", self._circuit_open_handler
        )
        self.encryption_circuit_breaker.add_event_listener(
            "half_open", self._circuit_half_open_handler
        )

    def _circuit_failure_handler(self, cb, exc):
        """
        Handle circuit breaker failure event.

        Args:
            cb: CircuitBreaker instance.
            exc: Exception that caused the failure.
        """
        logger.warning(f"CircuitBreaker '{cb.name}' recorded a failure: {exc}")
        if self.alerting:
            asyncio.create_task(
                self.alerting.send_alert(
                    f"CircuitBreaker '{cb.name}' recorded a failure: {exc}"
                )
            )

    def _circuit_open_handler(self, cb):
        """
        Handle circuit breaker open event.

        Args:
            cb: CircuitBreaker instance.
        """
        logger.warning(f"CircuitBreaker '{cb.name}' is now OPEN.")
        if self.alerting:
            asyncio.create_task(
                self.alerting.send_alert(f"CircuitBreaker '{cb.name}' is now OPEN.")
            )

    def _circuit_half_open_handler(self, cb):
        """
        Handle circuit breaker half-open event.

        Args:
            cb: CircuitBreaker instance.
        """
        logger.info(
            f"CircuitBreaker '{cb.name}' is now HALF-OPEN. Testing service availability."
        )
        if self.alerting:
            asyncio.create_task(
                self.alerting.send_alert(
                    f"CircuitBreaker '{cb.name}' is now HALF-OPEN. Testing service availability."
                )
            )

    def get_aws_circuit_breaker(self) -> CircuitBreaker:
        """
        Get the AWS Secrets Manager circuit breaker.

        Returns:
            CircuitBreaker: AWS Secrets Manager circuit breaker.
        """
        return self.aws_circuit_breaker

    def get_redis_circuit_breaker(self) -> CircuitBreaker:
        """
        Get the Redis circuit breaker.

        Returns:
            CircuitBreaker: Redis circuit breaker.
        """
        return self.redis_circuit_breaker

    def get_encryption_circuit_breaker(self) -> CircuitBreaker:
        """
        Get the Encryption circuit breaker.

        Returns:
            CircuitBreaker: Encryption circuit breaker.
        """
        return self.encryption_circuit_breaker


def with_circuit_breaker(
    get_circuit_breaker: Callable[[Any], Optional[CircuitBreaker]]
):
    """
    Decorator to apply a circuit breaker to a function.

    Args:
        get_circuit_breaker (Callable[[Any], Optional[CircuitBreaker]]): Function to retrieve the appropriate circuit breaker.

    Returns:
        Callable: Decorated function with circuit breaker applied.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            circuit_breaker = get_circuit_breaker(self)
            if not circuit_breaker:
                return await func(self, *args, **kwargs)
            return await circuit_breaker.call(func, self, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            circuit_breaker = get_circuit_breaker(self)
            if not circuit_breaker:
                return func(self, *args, **kwargs)
            return circuit_breaker.call(func, self, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
