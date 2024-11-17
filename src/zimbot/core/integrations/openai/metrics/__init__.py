# src/zimbot/core/integrations/openai/metrics/__init__.py

from prometheus_client import Counter, Gauge

ACTIVE_CLIENTS = Gauge("openai_active_clients", "Number of active OpenAI clients")

CLIENT_ERRORS = Counter(
    "openai_client_errors_total",
    "Total number of errors in OpenAI clients",
    ["error_type"],
)

CLIENT_USAGE = Counter(
    "openai_client_usage_total",
    "Total number of requests to OpenAI clients",
    ["client_type"],
)

ERROR_RATES = Counter(
    "openai_error_rates_total",
    "Total number of errors by model and error type",
    ["model", "error_type"],
)

RETRY_COUNT = Counter(
    "openai_retry_count_total", "Total number of retries in OpenAI clients"
)
