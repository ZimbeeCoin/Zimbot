#!/usr/bin/env python3
"""
Authentication Module

This module provides authentication endpoints and utilities for user
authentication, password hashing, and JWT generation within the FastAPI framework.
It includes the following features:

- JWT token generation and refresh
- User login endpoint with OAuth2 scheme
- Password hashing and verification
- Protected routes that require user authentication
- User registration with password policy enforcement
- Rate limiting to prevent brute-force attacks
- Mock user database (to be replaced with real database integration)

Dependencies:
- FastAPI, jose, passlib, pydantic, slowapi, email-validator

Usage:
    Import this module and include the router in the main FastAPI app.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from zimbot.core.config.settings import settings
from zimbot.core.integrations.exceptions import AuthenticationError
from zimbot.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Mock user database (Replace with real database integration)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("Secret123!"),
        "disabled": False,
    }
}


# Pydantic Models
class Token(BaseModel):
    """
    Represents a JWT access token.

    Attributes:
        access_token (str): The JWT token string.
        token_type (str): The type of token (usually "bearer").
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Represents the data stored in a JWT token.

    Attributes:
        username (Optional[str]): The username encoded in the JWT token.
    """

    username: Optional[str] = None


class User(BaseModel):
    """
    Represents a user model for authentication.

    Attributes:
        username (str): The user's username.
        email (EmailStr): The user's email address.
        full_name (Optional[str]): The user's full name.
        disabled (Optional[bool]): Indicates if the user account is disabled.
    """

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """
    Represents a user model stored in the database, including hashed password.

    Attributes:
        hashed_password (str): The hashed password for the user.
    """

    hashed_password: str


class UserCreate(BaseModel):
    """
    Represents the data required to create a new user.

    Attributes:
        username (str): The desired username for the new user.
        email (EmailStr): The email address for the new user.
        full_name (Optional[str]): The full name of the new user.
        password (str): The desired password for the new user.
    """

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str

    @validator("password")
    def password_strength(cls, v: str) -> str:
        """
        Validate the strength of the provided password.

        Args:
            v (str): The password string to validate.

        Returns:
            str: The validated password.

        Raises:
            ValueError: If the password does not meet strength requirements.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(char in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for char in v):
            raise ValueError("Password must contain at least one special character.")
        return v


# Dependency: User Database Access (Replace with real database integration)
async def get_user(username: str) -> Optional[UserInDB]:
    """
    Retrieve a user from the database.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        Optional[UserInDB]: The user object with database information, or None if not found.

    Raises:
        AuthenticationError: If there is an error accessing the user data.
    """
    try:
        user = fake_users_db.get(username)
        if user:
            return UserInDB(**user)
        return None
    except Exception as e:
        logger.error(f"Error retrieving user '{username}': {e}")
        raise AuthenticationError("Failed to retrieve user information", service="auth")


# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user credentials.

    Args:
        username (str): The username of the user.
        password (str): The plain text password of the user.

    Returns:
        Optional[UserInDB]: The authenticated user object if successful, else None.

    Raises:
        AuthenticationError: Raised if there is an error during authentication.
        HTTPException: Raised if the user account is inactive.
    """
    try:
        user = await get_user(username)
        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found.")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(
                f"Authentication failed: Incorrect password for user '{username}'."
            )
            return None
        if user.disabled:
            logger.warning(f"Authentication failed: User '{username}' is disabled.")
            raise AuthenticationError("Inactive user", service="auth")
        return user
    except Exception as e:
        logger.error(f"Authentication error for user '{username}': {e}")
        raise AuthenticationError(
            "Authentication failed due to an internal error", service="auth"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to include in the token payload.
        expires_delta (Optional[timedelta]): The token's expiration time.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


async def create_user(user_create: UserCreate) -> UserInDB:
    """
    Create a new user in the database.

    Args:
        user_create (UserCreate): The user data for creating a new user.

    Returns:
        UserInDB: The created user object with hashed password.

    Raises:
        HTTPException: If the username already exists or there is a database error.
    """
    if user_create.username in fake_users_db:
        logger.warning(
            f"User creation failed: Username '{user_create.username}' already exists."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    try:
        hashed_password = get_password_hash(user_create.password)
        user_dict = user_create.dict()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password
        user_dict["disabled"] = False
        fake_users_db[user_create.username] = user_dict
        logger.info(f"User created successfully: {user_create.username}")
        return UserInDB(**user_dict)
    except Exception as e:
        logger.error(f"Error creating user '{user_create.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed",
        )


# Dependency: Get Current User
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Decode JWT token and retrieve the current user.

    Args:
        token (str): The JWT token extracted from the Authorization header.

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
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            logger.error("JWT token missing 'sub' field.")
            raise credentials_exception
        # Inform type checker that username is not None
        username = cast(str, username)
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        logger.error(f"User '{token_data.username}' not found.")
        raise credentials_exception
    if user.disabled:
        logger.warning(f"User '{user.username}' is inactive.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return user


# Utility: Check if Current User is Active
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user is active.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        User: The active authenticated user.

    Raises:
        HTTPException: Raised if the user's account is inactive.
    """
    if current_user.disabled:
        logger.warning(f"Inactive user attempted access: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


# Token Generation Endpoint
@router.post("/token", response_model=Token)
@limiter.limit("5/minute")  # Rate limit to 5 requests per minute per IP
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate user and provide a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        Token: A JWT access token and its type.

    Raises:
        HTTPException: Raised if authentication fails due to incorrect credentials.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"User authenticated successfully: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


# Refresh Token Endpoint
@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")  # Rate limit to 10 requests per minute per IP
async def refresh_access_token(
    current_user: User = Depends(get_current_user),
):
    """
    Refresh the JWT access token.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        Token: A new JWT access token and its type.

    Raises:
        HTTPException: Raised if token refreshing fails due to authentication issues.
    """
    try:
        access_token_expires = timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        access_token = create_access_token(
            data={"sub": current_user.username},
            expires_delta=access_token_expires,
        )
        logger.info(f"Access token refreshed for user: {current_user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Failed to refresh token for user '{current_user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


# Example Protected Route
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Retrieve information about the current authenticated user.

    Args:
        current_user (User): The currently authenticated and active user.

    Returns:
        User: The authenticated user's profile information.
    """
    return current_user


# User Registration Endpoint
@router.post("/register", response_model=User)
@limiter.limit("2/minute")  # Rate limit to 2 registrations per minute per IP
async def register_user(user_create: UserCreate):
    """
    Register a new user with the provided details.

    Args:
        user_create (UserCreate): The user data for creating a new user.

    Returns:
        User: The created user's profile information.

    Raises:
        HTTPException: Raised if the username already exists or user creation fails.
    """
    try:
        new_user = await create_user(user_create)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error registering user '{user_create.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed",
        )
