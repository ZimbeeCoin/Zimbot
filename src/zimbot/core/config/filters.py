# src/zimbot/core/config/filters.py

import logging
import re


class MaskSensitiveFilter(logging.Filter):
    """
    Filters sensitive information from log records.
    """

    def __init__(self):
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        # Example pattern to mask API keys or tokens
        if hasattr(record, "message"):
            record.message = re.sub(
                r"(?i)(apikey|api_key|secret_key|token)\s*=\s*\S+",
                r"\1=****",
                record.message,
            )
        return True


class MetadataFilter(logging.Filter):
    """
    Injects service-level metadata into log records.
    """

    def __init__(self, service_name: str, instance_id: str, environment: str):
        super().__init__()
        self.service_name = service_name
        self.instance_id = instance_id
        self.environment = environment

    def filter(self, record: logging.LogRecord) -> bool:
        record.service_name = self.service_name
        record.instance_id = self.instance_id
        record.environment = self.environment
        return True
