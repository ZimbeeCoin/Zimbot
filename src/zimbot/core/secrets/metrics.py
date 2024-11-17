# src/core/secrets/metrics.py

"""
Prometheus metrics setup for secrets management.
"""

import logging
import threading
import time
from typing import Any, Dict, Optional

from prometheus_client import Counter, Histogram, start_http_server

logger = logging.getLogger(__name__)


class Metrics:
    """
    Handles Prometheus metrics for SecretsManager.
    """

    def __init__(self):
        """
        Initialize Prometheus metrics.
        """
        try:
            self.secret_retrieval_latency = Histogram(
                "secret_retrieval_latency_seconds",
                "Latency of secret retrieval operations",
                ["operation"],
            )
            self.secret_retrieval_errors = Counter(
                "secret_retrieval_errors_total",
                "Total number of errors during secret retrieval",
                ["operation"],
            )
            self.cache_hit_counter = Counter(
                "secret_cache_hits_total",
                "Total number of cache hits",
                ["cache_type"],
            )
            self.cache_miss_counter = Counter(
                "secret_cache_misses_total",
                "Total number of cache misses",
                ["cache_type"],
            )
            self.circuit_breaker_trips = Counter(
                "circuit_breaker_trips_total",
                "Total number of times circuit breakers have tripped",
                ["circuit_breaker"],
            )
            self.circuit_breaker_resets = Counter(
                "circuit_breaker_resets_total",
                "Total number of times circuit breakers have reset",
                ["circuit_breaker"],
            )
            logger.debug("Prometheus metrics initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Prometheus metrics: {e}")
            self.secret_retrieval_latency = None
            self.secret_retrieval_errors = None
            self.cache_hit_counter = None
            self.cache_miss_counter = None
            self.circuit_breaker_trips = None
            self.circuit_breaker_resets = None

        # For rate limiting metrics
        self._metric_locks = {}
        self._metric_timestamps = {}
        self._metric_counts = {}
        self._rate_limit_lock = threading.Lock()

    def start_metrics_server(self, port: int = 8000):
        """
        Start the Prometheus metrics HTTP server.

        Args:
            port (int): Port number to expose metrics.
        """
        try:
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}.")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")

    def adjust_circuit_breaker_thresholds(self, circuit_breaker_manager):
        """
        Dynamically adjust circuit breaker thresholds based on failure rates.

        Args:
            circuit_breaker_manager (CircuitBreakerManager): The circuit breaker manager instance.
        """
        try:
            # Calculate failure rate
            total_errors = sum(
                self.secret_retrieval_errors.labels(operation=op).count
                for op in ["sync", "async"]
            )
            total_requests = sum(
                self.secret_retrieval_latency.labels(operation=op)._sum.get()
                for op in ["sync", "async"]
            )

            if total_requests == 0:
                failure_rate = 0.0
            else:
                failure_rate = total_errors / total_requests

            logger.debug(f"Calculated failure rate: {failure_rate:.2%}")

            # Adjust thresholds for each circuit breaker
            for (
                circuit_breaker_name
            ) in circuit_breaker_manager.get_circuit_breaker_names():
                circuit_breaker = circuit_breaker_manager.get_circuit_breaker(
                    circuit_breaker_name
                )
                with circuit_breaker.lock:
                    if failure_rate > 0.8:
                        # Increase failure threshold or adjust recovery timeout
                        circuit_breaker.failure_threshold += 1
                        circuit_breaker.recovery_timeout = int(
                            circuit_breaker.recovery_timeout * 1.5
                        )
                        logger.info(
                            f"Increased thresholds for '{circuit_breaker_name}' due to high failure rate."
                        )
                    elif (
                        failure_rate < 0.2
                        and circuit_breaker.failure_threshold
                        > circuit_breaker.initial_failure_threshold
                    ):
                        # Decrease failure threshold or adjust recovery timeout
                        circuit_breaker.failure_threshold = max(
                            circuit_breaker.failure_threshold - 1,
                            circuit_breaker.initial_failure_threshold,
                        )
                        circuit_breaker.recovery_timeout = max(
                            int(circuit_breaker.recovery_timeout / 1.5),
                            circuit_breaker.initial_recovery_timeout,
                        )
                        logger.info(
                            f"Decreased thresholds for '{circuit_breaker_name}' due to low failure rate."
                        )
        except Exception as e:
            logger.error(
                f"Failed to adjust circuit breaker thresholds: {e}", exc_info=True
            )

    def rate_limit_metric(
        self,
        metric: Counter,
        labels: Dict[str, Any],
        increment: float = 1.0,
        rate_limit: int = 10,
    ):
        """
        Increment a Prometheus counter with rate limiting.

        Args:
            metric (Counter): The Prometheus counter to increment.
            labels (Dict[str, Any]): Labels for the counter.
            increment (float): The amount to increment by.
            rate_limit (int): Maximum increments allowed per second.
        """
        metric_key = (metric._name, tuple(sorted(labels.items())))

        with self._rate_limit_lock:
            # Initialize counters if they don't exist
            if metric_key not in self._metric_counts:
                self._metric_counts[metric_key] = 0
                self._metric_timestamps[metric_key] = time.time()
                self._metric_locks[metric_key] = threading.Lock()

        with self._metric_locks[metric_key]:
            current_time = time.time()
            elapsed_time = current_time - self._metric_timestamps[metric_key]

            if elapsed_time >= 1.0:
                # Reset counters after one second
                self._metric_counts[metric_key] = 0
                self._metric_timestamps[metric_key] = current_time

            if self._metric_counts[metric_key] < rate_limit:
                metric.labels(**labels).inc(increment)
                self._metric_counts[metric_key] += 1
            else:
                logger.debug(
                    f"Rate limit reached for metric '{metric._name}' with labels {labels}. Increment skipped."
                )
