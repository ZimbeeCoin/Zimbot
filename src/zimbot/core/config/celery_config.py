# src/zimbot/core/config/celery_config.py

from pydantic import Field

from .base import BaseConfig


class CelerySettings(BaseConfig):
    broker_url: str = Field(
        default=...,
        validation_alias="CELERY_BROKER_URL",
        description="Celery broker URL",
    )
    result_backend: str = Field(
        default=...,
        validation_alias="CELERY_RESULT_BACKEND",
        description="Celery result backend URL",
    )
    worker_count: int = Field(
        default=4,
        validation_alias="CELERY_WORKER_COUNT",
        description="Number of Celery workers",
    )

    model_config = BaseConfig.model_config
