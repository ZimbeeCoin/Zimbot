# src/zimbot/core/secrets/__init__.py

"""
Secrets Management Package.
"""

from .alerting import Alerting
from .caching import Caching
from .client import AWSSecretsManagerClient
from .decorators import measure_latency_async, measure_latency_sync
from .encryption import EncryptionManager
from .error_handling import handle_client_error_async, handle_client_error_sync
from .exceptions import MaxRetriesExceededError, MissingSecretError
from .metrics import Metrics
from .secrets_logger import get_logger
from .secrets_manager import SecretsManager

__all__ = [
    "Alerting",
    "Caching",
    "AWSSecretsManagerClient",
    "EncryptionManager",
    "measure_latency_sync",
    "measure_latency_async",
    "handle_client_error_async",
    "handle_client_error_sync",
    "MissingSecretError",
    "MaxRetriesExceededError",
    "Metrics",
    "get_logger",
    "SecretsManager",
]
