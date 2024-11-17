# src/core/integrations/openai/metrics.py

import logging
import time
from typing import Any, Dict, Optional

import sentry_sdk
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class OpenAIMetrics:
    """Enhanced metrics tracking for OpenAI operations"""

    # Define metrics
    request_counter = Counter(
        "openai_requests_total",
        "Total OpenAI API requests",
        ["endpoint", "model", "status"],
    )

    latency_histogram = Histogram(
        "openai_request_duration_seconds",
        "OpenAI API request duration in seconds",
        ["endpoint", "model"],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
    )

    token_usage = Counter(
        "openai_token_usage_total",
        "Total token usage",
        ["model", "type"],  # type: prompt, completion
    )

    streaming_chunks = Counter(
        "openai_streaming_chunks_total",
        "Total streaming chunks processed",
        ["model"],
    )

    active_streams = Gauge(
        "openai_active_streams",
        "Currently active streaming connections",
        ["model"],
    )

    model_availability = Gauge(
        "openai_model_availability", "Model availability status", ["model"]
    )

    rate_limit_remaining = Gauge(
        "openai_rate_limit_remaining", "Remaining API rate limit", ["endpoint"]
    )

    @classmethod
    async def track_request(
        cls,
        endpoint: str,
        model: str,
        status: str,
        duration: float,
        token_usage: Optional[Dict[str, int]] = None,
    ):
        """
        Track a complete API request with all metrics.

        Args:
            endpoint (str): The API endpoint being called.
            model (str): The OpenAI model used.
            status (str): The status of the request ('success' or 'error').
            duration (float): Duration of the request in seconds.
            token_usage (Optional[Dict[str, int]]): Token usage details.
        """
        try:
            # Increment request counter
            cls.request_counter.labels(
                endpoint=endpoint, model=model, status=status
            ).inc()

            # Record request duration
            cls.latency_histogram.labels(endpoint=endpoint, model=model).observe(
                duration
            )

            # Record token usage if available
            if token_usage:
                if "prompt_tokens" in token_usage:
                    cls.token_usage.labels(model=model, type="prompt").inc(
                        token_usage["prompt_tokens"]
                    )

                if "completion_tokens" in token_usage:
                    cls.token_usage.labels(model=model, type="completion").inc(
                        token_usage["completion_tokens"]
                    )
        except Exception as e:
            logger.error(f"Failed to track OpenAI request metrics: {e}")
            sentry_sdk.capture_exception(e)

    @classmethod
    def start_stream(cls, model: str):
        """
        Track the start of a streaming connection.

        Args:
            model (str): The OpenAI model being used.
        """
        cls.active_streams.labels(model=model).inc()

    @classmethod
    def end_stream(cls, model: str):
        """
        Track the end of a streaming connection.

        Args:
            model (str): The OpenAI model being used.
        """
        cls.active_streams.labels(model=model).dec()

    @classmethod
    def update_model_availability(cls, model: str, available: bool):
        """
        Update model availability status.

        Args:
            model (str): The OpenAI model.
            available (bool): Availability status.
        """
        cls.model_availability.labels(model=model).set(1 if available else 0)

    @classmethod
    def update_rate_limit(cls, endpoint: str, remaining: int):
        """
        Update remaining rate limit.

        Args:
            endpoint (str): The API endpoint.
            remaining (int): Remaining rate limit count.
        """
        cls.rate_limit_remaining.labels(endpoint=endpoint).set(remaining)


class MetricsContext:
    """Context manager for tracking request metrics"""

    def __init__(self, endpoint: str, model: str, streaming: bool = False):
        self.endpoint = endpoint
        self.model = model
        self.streaming = streaming
        self.start_time = None

    async def __aenter__(self):
        self.start_time = time.time()
        if self.streaming:
            OpenAIMetrics.start_stream(self.model)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "error" if exc_type else "success"

        await OpenAIMetrics.track_request(
            endpoint=self.endpoint,
            model=self.model,
            status=status,
            duration=duration,
        )

        if self.streaming:
            OpenAIMetrics.end_stream(self.model)
