"""
API package containing FastAPI route definitions and router aggregation.

This module provides a centralized collection of all API routers for easy
inclusion in the main application. Each router is mapped to its URL prefix.

Usage:
    from zimbot.api import ROUTERS

    # Register all routes with FastAPI app
    for prefix, router in ROUTERS.items():
        app.include_router(router, prefix=f"/{prefix}", tags=[prefix.capitalize()])
"""

from typing import Dict

from fastapi import APIRouter

# Import routers from individual modules
from .auth import router as auth_router
from .consult import router as consult_router
from .health import router as health_router
from .market import router as market_router
from .subscriptions import router as subscriptions_router

# Centralized dictionary for all API routes with prefixes
ROUTERS: Dict[str, APIRouter] = {
    "auth": auth_router,  # Authentication and authorization
    "consult": consult_router,  # User consultation services
    "health": health_router,  # Health and diagnostics
    "market": market_router,  # Market data endpoints
    "subscriptions": subscriptions_router,  # Subscription management
}

# Public API surface - exposing only ROUTERS for simplicity in main app inclusion
__all__ = ["ROUTERS"]
