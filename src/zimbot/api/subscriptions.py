# src/zimbot/api/subscriptions.py
"""
Subscription Management API

This module provides endpoints for managing user subscriptions. It includes
functionality for creating new subscriptions, listing user subscriptions, and
potentially updating or deleting subscriptions in the future.

Dependencies:
    - FastAPI: Provides routing and exception handling.
    - Database (SQLAlchemy or similar): Manages persistent storage of subscriptions.
    - Authentication: Only authenticated users can create subscriptions.

Endpoints:
    - POST /subscriptions/: Creates a new subscription for a specified user.
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

from zimbot.core.auth.services.auth_service import (  # Import authentication dependency
    get_current_user,
)
from zimbot.core.utils.logger import get_logger
from zimbot.database import get_db  # Placeholder for database session
from zimbot.models import Subscription  # Placeholder for SQLAlchemy model

logger = get_logger(__name__)
router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# Define input validation model
class SubscriptionCreate(BaseModel):
    user_id: int
    plan: constr(strip_whitespace=True, min_length=3)


@router.post("/", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Create a new subscription for a user.

    Args:
        subscription_data (SubscriptionCreate): Input model with `user_id` and `plan`.
        db (Session): Database session dependency for accessing the database.
        current_user (dict): The currently authenticated user, injected via dependency.

    Returns:
        Dict[str, str]: Details of the created subscription, including user ID, plan, and status.

    Raises:
        HTTPException: 400 error for invalid plan, 500 error for unexpected failures.
    """
    valid_plans = ["basic", "premium", "pro"]
    if subscription_data.plan not in valid_plans:
        logger.warning(f"Invalid plan '{subscription_data.plan}' attempted.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {subscription_data.plan}. Available plans are: {', '.join(valid_plans)}",
        )

    try:
        # Placeholder for actual subscription creation logic with database
        new_subscription = Subscription(
            user_id=subscription_data.user_id,
            plan=subscription_data.plan,
            status="active",
        )
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)

        logger.info(
            f"Created subscription for user {subscription_data.user_id} with plan '{subscription_data.plan}'"
        )
        return {
            "user_id": str(new_subscription.user_id),
            "plan": new_subscription.plan,
            "status": new_subscription.status,
        }

    except Exception as e:
        logger.error(
            f"Failed to create subscription for user {subscription_data.user_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subscription creation failed.",
        )
