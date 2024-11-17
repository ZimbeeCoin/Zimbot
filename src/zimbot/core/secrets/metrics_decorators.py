# src/core/secrets/metrics_decorators.py

import asyncio
import functools
import time
from typing import Callable, Optional, TypeVar

from prometheus_client import Counter, Histogram

T = TypeVar("T", bound=Callable[..., any])


def measure_latency_sync(
    func: T,
    counter: Optional[Counter] = None,
    histogram: Optional[Histogram] = None,
    failure_counter: Optional[Counter] = None,
    high_latency_threshold: Optional[float] = None,
    high_latency_counter: Optional[Counter] = None,
) -> T:
    """
    Decorator to measure latency of synchronous functions and record metrics.

    Args:
        func (Callable): The function to decorate.
        counter (Optional[Counter]): Prometheus counter to increment.
        histogram (Optional[Histogram]): Prometheus histogram to observe latency.
        failure_counter (Optional[Counter]): Prometheus counter to increment on failure.
        high_latency_threshold (Optional[float]): Latency threshold in seconds to count as high latency.
        high_latency_counter (Optional[Counter]): Prometheus counter to increment on high latency.

    Returns:
        Callable: The decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            if failure_counter:
                failure_counter.inc()
            raise
        finally:
            end_time = time.time()
            latency = end_time - start_time
            if counter:
                counter.inc()
            if histogram:
                histogram.observe(latency)
            if high_latency_threshold and latency > high_latency_threshold:
                if high_latency_counter:
                    high_latency_counter.inc()

    return wrapper  # type: ignore


def measure_latency_async(
    func: Callable[..., asyncio.Future],
    counter: Optional[Counter] = None,
    histogram: Optional[Histogram] = None,
    failure_counter: Optional[Counter] = None,
    high_latency_threshold: Optional[float] = None,
    high_latency_counter: Optional[Counter] = None,
) -> Callable[..., asyncio.Future]:
    """
    Decorator to measure latency of asynchronous functions and record metrics.

    Args:
        func (Callable): The async function to decorate.
        counter (Optional[Counter]): Prometheus counter to increment.
        histogram (Optional[Histogram]): Prometheus histogram to observe latency.
        failure_counter (Optional[Counter]): Prometheus counter to increment on failure.
        high_latency_threshold (Optional[float]): Latency threshold in seconds to count as high latency.
        high_latency_counter (Optional[Counter]): Prometheus counter to increment on high latency.

    Returns:
        Callable: The decorated async function.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            if failure_counter:
                failure_counter.inc()
            raise
        finally:
            end_time = time.time()
            latency = end_time - start_time
            if counter:
                counter.inc()
            if histogram:
                histogram.observe(latency)
            if high_latency_threshold and latency > high_latency_threshold:
                if high_latency_counter:
                    high_latency_counter.inc()

    return wrapper


def measure_latency(
    func: T,
    counter: Optional[Counter] = None,
    histogram: Optional[Histogram] = None,
    failure_counter: Optional[Counter] = None,
    high_latency_threshold: Optional[float] = None,
    high_latency_counter: Optional[Counter] = None,
) -> T:
    """
    General decorator to measure latency for both sync and async functions.

    Args:
        func (Callable): The function to decorate.
        counter (Optional[Counter]): Prometheus counter to increment.
        histogram (Optional[Histogram]): Prometheus histogram to observe latency.
        failure_counter (Optional[Counter]): Prometheus counter to increment on failure.
        high_latency_threshold (Optional[float]): Latency threshold in seconds to count as high latency.
        high_latency_counter (Optional[Counter]): Prometheus counter to increment on high latency.

    Returns:
        Callable: The decorated function.
    """
    if asyncio.iscoroutinefunction(func):
        return measure_latency_async(
            func,
            counter=counter,
            histogram=histogram,
            failure_counter=failure_counter,
            high_latency_threshold=high_latency_threshold,
            high_latency_counter=high_latency_counter,
        )
    else:
        return measure_latency_sync(
            func,
            counter=counter,
            histogram=histogram,
            failure_counter=failure_counter,
            high_latency_threshold=high_latency_threshold,
            high_latency_counter=high_latency_counter,
        )  # type: ignore


# Example Prometheus metrics
secret_retrieval_counter = Counter(
    "secret_retrievals_total", "Total number of secrets retrieved"
)
secret_latency_histogram = Histogram(
    "secret_retrieval_latency_seconds", "Latency of secret retrieval in seconds"
)
secret_failure_counter = Counter(
    "secret_retrieval_failures_total",
    "Total number of failed secret retrieval attempts",
)
secret_high_latency_counter = Counter(
    "secret_retrieval_high_latency_total",
    "Total number of secret retrievals exceeding latency thresholds",
)


# Convenience decorators with predefined metrics and thresholds
def measure_latency_sync_with_metrics(func: T) -> T:
    """
    Synchronous latency decorator with predefined Prometheus metrics.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """
    return measure_latency(
        func,
        counter=secret_retrieval_counter,
        histogram=secret_latency_histogram,
        failure_counter=secret_failure_counter,
        high_latency_threshold=2.0,  # Example threshold in seconds
        high_latency_counter=secret_high_latency_counter,
    )  # type: ignore


def measure_latency_async_with_metrics(
    func: Callable[..., asyncio.Future]
) -> Callable[..., asyncio.Future]:
    """
    Asynchronous latency decorator with predefined Prometheus metrics.

    Args:
        func (Callable): The async function to decorate.

    Returns:
        Callable: The decorated async function.
    """
    return measure_latency(
        func,
        counter=secret_retrieval_counter,
        histogram=secret_latency_histogram,
        failure_counter=secret_failure_counter,
        high_latency_threshold=2.0,  # Example threshold in seconds
        high_latency_counter=secret_high_latency_counter,
    )
