# src/core/secrets/decorators.py

"""
Decorators for measuring and logging the latency of functions.
"""

import asyncio
import logging
import time
from typing import Any, Callable

from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)


def measure_latency_sync(func: Callable) -> Callable:
    """
    Decorator to measure and log the latency of synchronous functions.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The wrapped function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            latency = end_time - start_time
            logger.debug(
                f"Function '{func.__name__}' executed in {latency:.4f} seconds."
            )
            if hasattr(func, "prometheus_counter") and isinstance(
                func.prometheus_counter, Counter
            ):
                func.prometheus_counter.labels(operation=func.__name__).inc()

    return wrapper


def measure_latency_async(func: Callable) -> Callable:
    """
    Decorator to measure and log the latency of asynchronous functions.

    Args:
        func (Callable): The coroutine function to decorate.

    Returns:
        Callable: The wrapped coroutine.
    """

    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            latency = end_time - start_time
            logger.debug(
                f"Async function '{func.__name__}' executed in {latency:.4f} seconds."
            )
            if hasattr(func, "prometheus_counter") and isinstance(
                func.prometheus_counter, Counter
            ):
                func.prometheus_counter.labels(operation=func.__name__).inc()

    return wrapper
