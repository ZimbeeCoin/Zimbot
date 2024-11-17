# src/zimbot/core/auth/auth_dependencies.py

from typing import AsyncGenerator

import aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from zimbot.core.auth.schemas.types import TokenData, User
from zimbot.core.auth.services.auth_service import AuthService
from zimbot.core.config.settings import settings
from zimbot.core.utils.logger import get_logger
from zimbot.database import get_db_session  # Replace with your actual DB dependency

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """
    Dependency to get a Redis client.

    Yields:
        aioredis.Redis: An instance of the Redis client.
    """
    redis = aioredis.from_url(
        settings.redis.url,
        encoding="utf8",
        decode_responses=True,
        max_connections=10,
    )
    try:
        yield redis
    finally:
        await redis.close()


async def get_auth_service(
    redis: aioredis.Redis = Depends(get_redis), db_session=Depends(get_db_session)
) -> AuthService:
    """
    Dependency to get an instance of AuthService.

    Args:
        redis (aioredis.Redis): Redis client instance.
        db_session: Database session instance.

    Returns:
        AuthService: An initialized AuthService instance.
    """
    auth_service = AuthService(redis=redis, db_session=db_session)
    return auth_service


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Decode JWT token and retrieve the current user.

    Args:
        token (str): The JWT token extracted from the Authorization header.
        auth_service (AuthService): The authentication service instance.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: Raised if token validation fails or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth_service.decode_token(token)
        username = payload.get("sub")
        if not isinstance(username, str):
            logger.error("JWT token missing 'sub' field or 'sub' is not a string.")
            raise credentials_exception
        token_data = TokenData(username=username)
    except (JWTError, ValidationError) as e:
        logger.error(f"JWT decoding error: {e}")
        raise credentials_exception

    user_in_db = await auth_service.get_user(username=token_data.username)
    if user_in_db is None:
        logger.error(f"User '{token_data.username}' not found.")
        raise credentials_exception
    if user_in_db.disabled:
        logger.warning(f"User '{user_in_db.username}' is inactive.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    user = User(**user_in_db.dict())
    return user
