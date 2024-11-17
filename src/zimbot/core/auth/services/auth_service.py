# src/zimbot/core/auth/services/auth_service.py

import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from zimbot.core.auth.schemas.types import RefreshTokenData, Token, TokenData, UserInDB
from zimbot.core.config.settings import Settings, get_settings
from zimbot.core.integrations.email.email_service import EmailService
from zimbot.core.integrations.exceptions.exceptions import (
    InvalidCredentialsError,
    MFASetupError,
    MFAValidationError,
    PasswordResetError,
    RedisConnectionError,
    RedisOperationError,
    TokenBlacklistedError,
    TokenRevokedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from zimbot.core.integrations.redis.redis_utils import RedisClient
from zimbot.models.user import RefreshToken
from zimbot.models.user import User as DBUser

logger = logging.getLogger(__name__)

# Initialize settings
settings: Settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration from settings
ALGORITHM = settings.jwt.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt.refresh_token_expire_days

# Token Blacklist Key from settings
TOKEN_BLACKLIST_KEY = settings.jwt.token_blacklist_key


class AuthService:
    def __init__(self, redis: RedisClient, db_session: AsyncSession) -> None:
        """
        Initialize the AuthService with Redis and Database Session.

        Args:
            redis (RedisClient): The Redis client instance for caching and token management.
            db_session (AsyncSession): The SQLAlchemy asynchronous database session.
        """
        self.redis = redis
        self.db = db_session
        self.email_service = EmailService()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hashed version.

        Args:
            plain_password (str): The user's plain text password.
            hashed_password (str): The hashed password stored in the database.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)

    async def get_password_hash_async(self, password: str) -> str:
        """
        Asynchronously hash a plain text password using a thread pool.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self.get_password_hash, password
        )

    async def verify_password_async(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Asynchronously verify a plain password against its hashed version using a thread pool.

        Args:
            plain_password (str): The user's plain text password.
            hashed_password (str): The hashed password stored in the database.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self.verify_password, plain_password, hashed_password
        )

    async def authenticate_user(self, username: str, password: str) -> UserInDB:
        """
        Authenticate a user by username and password.

        Args:
            username (str): The username of the user attempting to authenticate.
            password (str): The plain text password provided by the user.

        Returns:
            UserInDB: The authenticated user's data.

        Raises:
            InvalidCredentialsError: If authentication fails due to invalid credentials.
        """
        user = await self.get_user(username)
        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found.")
            raise InvalidCredentialsError("Invalid username or password")
        if not await self.verify_password_async(password, user.hashed_password):
            logger.warning(
                f"Authentication failed: Incorrect password for user '{username}'."
            )
            raise InvalidCredentialsError("Invalid username or password")
        if user.disabled:
            logger.warning(f"Authentication failed: User '{username}' is disabled.")
            raise InvalidCredentialsError("Invalid username or password")
        return user

    async def get_user(self, username: str) -> Optional[UserInDB]:
        """
        Retrieve a user by username from the database and convert to UserInDB.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            Optional[UserInDB]: The user's data if found, None otherwise.
        """
        try:
            result = await self.db.execute(
                select(DBUser).where(DBUser.username == username)
            )
            db_user = result.scalars().first()
            if db_user:
                user_in_db = UserInDB(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    full_name=db_user.full_name,
                    hashed_password=db_user.hashed_password,
                    disabled=db_user.disabled,
                    mfa_enabled=db_user.mfa_enabled,
                    mfa_secret=db_user.mfa_secret,
                    wallet_address=db_user.wallet_address,
                    profile_settings=db_user.profile_settings,
                    roles=(
                        db_user.roles
                        if isinstance(db_user.roles, list)
                        else db_user.roles.split(",")
                    ),
                    portfolios=db_user.portfolios,
                    refresh_tokens=db_user.refresh_tokens,
                    sessions=db_user.sessions,
                )
                return user_in_db
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user '{username}': {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Retrieve a user by email from the database and convert to UserInDB.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            Optional[UserInDB]: The user's data if found, None otherwise.
        """
        try:
            result = await self.db.execute(select(DBUser).where(DBUser.email == email))
            db_user = result.scalars().first()
            if db_user:
                user_in_db = UserInDB(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    full_name=db_user.full_name,
                    hashed_password=db_user.hashed_password,
                    disabled=db_user.disabled,
                    mfa_enabled=db_user.mfa_enabled,
                    mfa_secret=db_user.mfa_secret,
                    wallet_address=db_user.wallet_address,
                    profile_settings=db_user.profile_settings,
                    roles=(
                        db_user.roles
                        if isinstance(db_user.roles, list)
                        else db_user.roles.split(",")
                    ),
                    portfolios=db_user.portfolios,
                    refresh_tokens=db_user.refresh_tokens,
                    sessions=db_user.sessions,
                )
                return user_in_db
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user by email '{email}': {e}")
            return None

    async def create_user(self, user_create: Dict[str, str]) -> UserInDB:
        """
        Create a new user in the database.

        Args:
            user_create (Dict[str, str]): A dictionary containing user creation data.

        Returns:
            UserInDB: The newly created user's data.

        Raises:
            UserAlreadyExistsError: If the username or email already exists.
        """
        existing_user = await self.get_user(user_create["username"])
        if existing_user:
            logger.warning(
                f"User creation failed: Username '{user_create['username']}' already exists."
            )
            raise UserAlreadyExistsError("Username already exists")

        existing_email = await self.get_user_by_email(user_create["email"])
        if existing_email:
            logger.warning(
                f"User creation failed: Email '{user_create['email']}' already exists."
            )
            raise UserAlreadyExistsError("Email already exists")

        # Hash the password asynchronously
        hashed_password = await self.get_password_hash_async(user_create["password"])
        new_user = DBUser(
            username=user_create["username"],
            email=user_create["email"],
            full_name=user_create.get("full_name"),
            hashed_password=hashed_password,
            disabled=False,
            mfa_enabled=False,
            wallet_address=user_create.get("wallet_address"),
            profile_settings={},  # Initialize as empty dict
            roles=["user"],
        )
        try:
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            logger.info(f"New user created: {new_user.username}")
            user_in_db = UserInDB(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                full_name=new_user.full_name,
                hashed_password=new_user.hashed_password,
                disabled=new_user.disabled,
                mfa_enabled=new_user.mfa_enabled,
                mfa_secret=new_user.mfa_secret,
                wallet_address=new_user.wallet_address,
                profile_settings=new_user.profile_settings,
                roles=new_user.roles,
                portfolios=new_user.portfolios,
                refresh_tokens=new_user.refresh_tokens,
                sessions=new_user.sessions,
            )
            return user_in_db
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating user '{user_create['username']}': {e}")
            raise UserAlreadyExistsError(
                "Failed to create user due to a database error"
            )

    def create_access_token(
        self,
        data: Dict[str, str],
        scopes: Optional[List[str]] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Generate a JWT access token with optional scopes.

        Args:
            data (Dict[str, str]): The data to include in the token payload.
            scopes (Optional[List[str]]): A list of scopes or permissions.
            expires_delta (Optional[timedelta]): Token expiration time.

        Returns:
            str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if scopes:
            to_encode.update({"scopes": scopes})
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(
            to_encode, settings.jwt.secret_key.get_secret_value(), algorithm=ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(self) -> str:
        """
        Generate a unique refresh token.

        Returns:
            str: A new refresh token.
        """
        return str(uuid.uuid4())

    async def generate_tokens(
        self, user: UserInDB, scopes: Optional[List[str]] = None
    ) -> Token:
        """
        Generate access and refresh tokens for a user with optional scopes.

        Args:
            user (UserInDB): The user for whom to generate tokens.
            scopes (Optional[List[str]]): A list of scopes or permissions.

        Returns:
            Token: A Pydantic model containing access and refresh tokens.

        Raises:
            InvalidCredentialsError: If token generation fails.
        """
        access_token = self.create_access_token(
            data={"sub": user.username},
            scopes=scopes,
        )
        refresh_token = self.create_refresh_token()
        try:
            # Create a new refresh token entry in the database
            refresh_token_entry = RefreshToken(
                token=refresh_token,
                user_id=user.id,
                expires_at=datetime.utcnow()
                + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                revoked=False,
            )
            self.db.add(refresh_token_entry)
            await self.db.commit()
            logger.info(f"Generated tokens for user: {user.username}")
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error generating tokens for user '{user.username}': {e}")
            raise InvalidCredentialsError("Failed to generate tokens")

    def decode_token(self, token: str) -> TokenData:
        """
        Decode a JWT token.

        Args:
            token (str): The JWT token to decode.

        Returns:
            TokenData: The decoded token payload.

        Raises:
            InvalidCredentialsError: If the token is invalid or cannot be decoded.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt.secret_key.get_secret_value(),
                algorithms=[ALGORITHM],
            )
            username: Optional[str] = payload.get("sub")
            scopes: Optional[List[str]] = payload.get("scopes", [])
            if username is None:
                logger.error("Token payload missing 'sub' field.")
                raise InvalidCredentialsError("Invalid token")
            token_data = TokenData(username=username, scopes=scopes)
            return token_data
        except JWTError as e:
            logger.error(f"Token decoding failed: {e}")
            raise InvalidCredentialsError("Invalid token")

    async def revoke_token(self, token: str) -> None:
        """
        Revoke a specific token by adding it to the blacklist.

        Args:
            token (str): The JWT token to revoke.

        Raises:
            TokenRevokedError: If the Redis client is not initialized or revoking fails.
        """
        if not self.redis:
            logger.error("Redis client is not initialized.")
            raise TokenRevokedError("Redis client not initialized.")
        try:
            await self.redis.sadd(TOKEN_BLACKLIST_KEY, token)
            logger.info(f"Token revoked: {token}")
        except RedisOperationError as e:
            logger.error(f"Failed to revoke token: {e}")
            raise TokenRevokedError(str(e))

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token (str): The JWT token to check.

        Returns:
            bool: True if the token is blacklisted, False otherwise.

        Raises:
            TokenBlacklistedError: If the Redis client is not initialized or checking fails.
        """
        if not self.redis:
            logger.error("Redis client is not initialized.")
            raise TokenBlacklistedError("Redis client not initialized.")
        try:
            return await self.redis.sismember(TOKEN_BLACKLIST_KEY, token)
        except RedisOperationError as e:
            logger.error(f"Failed to check token blacklist: {e}")
            raise TokenBlacklistedError(str(e))

    async def purge_expired_tokens(self) -> None:
        """
        Purge expired refresh tokens from the database.

        This method should be scheduled as a background task.
        """
        while True:
            try:
                current_time = datetime.utcnow()
                expired_tokens = await self.db.execute(
                    select(RefreshToken).where(
                        RefreshToken.expires_at < current_time,
                        RefreshToken.revoked == False,
                    )
                )
                tokens_to_delete = expired_tokens.scalars().all()
                if tokens_to_delete:
                    for token in tokens_to_delete:
                        token.revoked = True
                        self.db.add(token)
                    await self.db.commit()
                    logger.info(
                        f"Purged {len(tokens_to_delete)} expired refresh tokens."
                    )
                else:
                    logger.info("No expired refresh tokens found to purge.")
            except SQLAlchemyError as e:
                await self.db.rollback()
                logger.error(f"Error purging expired tokens: {e}")
            await asyncio.sleep(3600)  # Run every hour

    async def setup_mfa(self, user: UserInDB) -> Dict[str, str]:
        """
        Set up Multi-Factor Authentication (MFA) for a user.

        Args:
            user (UserInDB): The user for whom to set up MFA.

        Returns:
            Dict[str, str]: A dictionary containing the MFA secret and OTP URI.

        Raises:
            MFASetupError: If MFA setup fails.
        """
        try:
            secret = pyotp.random_base32()
            # Retrieve the DBUser instance
            db_user = await self.db.get(DBUser, user.id)
            if not db_user:
                logger.error(f"User '{user.username}' not found for MFA setup.")
                raise MFASetupError("User not found")
            db_user.mfa_enabled = True
            db_user.mfa_secret = secret
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            # Generate OTP URI for QR code
            otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=db_user.email, issuer_name="ZimbeeCoin"
            )

            # Send the MFA secret and OTP URI via email
            await self.email_service.send_mfa_setup_email(
                db_user.email, secret, otp_uri
            )
            logger.info(f"MFA setup initiated for user: {db_user.username}")

            return {"mfa_secret": secret, "otp_uri": otp_uri}
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error setting up MFA for user '{user.username}': {e}")
            raise MFASetupError("Failed to set up MFA")

    async def validate_mfa(self, user: UserInDB, token: str) -> bool:
        """
        Validate a MFA token provided by the user.

        Args:
            user (UserInDB): The user attempting to validate MFA.
            token (str): The MFA token provided by the user.

        Returns:
            bool: True if MFA token is valid, False otherwise.

        Raises:
            MFAValidationError: If validation fails due to incorrect token or other issues.
        """
        if not user.mfa_enabled or not user.mfa_secret:
            logger.warning(
                f"MFA validation failed: MFA not enabled for user '{user.username}'."
            )
            raise MFAValidationError("MFA not enabled for user.")
        try:
            totp = pyotp.TOTP(user.mfa_secret)
            is_valid = totp.verify(token, valid_window=1)  # Allows a 30-second window
            if not is_valid:
                logger.warning(
                    f"MFA validation failed: Invalid token for user '{user.username}'."
                )
                raise MFAValidationError("Invalid MFA token.")
            logger.info(f"MFA validation successful for user '{user.username}'.")
            return True
        except Exception as e:
            logger.error(f"MFA validation error for user '{user.username}': {e}")
            raise MFAValidationError("MFA validation failed.")

    async def initiate_password_reset(self, email: str) -> None:
        """
        Initiate a password reset process for a user by sending a reset email.

        Args:
            email (str): The email address of the user.

        Raises:
            UserNotFoundError: If no user with the provided email exists.
            PasswordResetError: If sending the reset email fails.
        """
        user = await self.get_user_by_email(email)
        if not user:
            logger.warning(
                f"Password reset initiation failed: User with email '{email}' not found."
            )
            raise UserNotFoundError("User not found")
        try:
            reset_token = (
                self.create_refresh_token()
            )  # Using refresh tokens as reset tokens
            expires_at = datetime.utcnow() + timedelta(
                hours=1
            )  # Reset token valid for 1 hour

            # Create a refresh token entry for the reset token
            reset_token_entry = RefreshToken(
                token=reset_token,
                user_id=user.id,
                expires_at=expires_at,
                revoked=False,
            )
            self.db.add(reset_token_entry)
            await self.db.commit()

            # Send the reset email with the token
            reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
            await self.email_service.send_password_reset_email(user.email, reset_link)
            logger.info(f"Password reset email sent to user '{user.username}'.")
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                f"Database error during password reset initiation for '{email}': {e}"
            )
            raise PasswordResetError("Failed to initiate password reset")
        except Exception as e:
            logger.error(f"Error sending password reset email to '{email}': {e}")
            raise PasswordResetError("Failed to send password reset email")

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        """
        Confirm and complete the password reset process.

        Args:
            token (str): The password reset token provided by the user.
            new_password (str): The new password to set.

        Raises:
            InvalidCredentialsError: If the token is invalid or expired.
            PasswordResetError: If updating the password fails.
        """
        try:
            # Validate the reset token
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.token == token,
                    RefreshToken.expires_at > datetime.utcnow(),
                    RefreshToken.revoked == False,
                )
            )
            reset_token_entry = result.scalars().first()
            if not reset_token_entry:
                logger.warning(
                    f"Password reset confirmation failed: Invalid or expired token '{token}'."
                )
                raise InvalidCredentialsError(
                    "Invalid or expired password reset token."
                )

            # Retrieve the associated user
            user = await self.db.get(DBUser, reset_token_entry.user_id)
            if not user:
                logger.error(
                    f"Password reset confirmation failed: User ID '{reset_token_entry.user_id}' not found."
                )
                raise PasswordResetError("User not found")

            # Update the user's password
            hashed_password = await self.get_password_hash_async(new_password)
            user.hashed_password = hashed_password
            self.db.add(user)

            # Revoke the reset token
            reset_token_entry.revoked = True
            self.db.add(reset_token_entry)

            await self.db.commit()

            # Optionally, send a confirmation email
            await self.email_service.send_password_reset_confirmation_email(user.email)
            logger.info(f"Password reset successful for user '{user.username}'.")
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                f"Database error during password reset confirmation with token '{token}': {e}"
            )
            raise PasswordResetError("Failed to reset password due to a database error")
        except Exception as e:
            logger.error(
                f"Error during password reset confirmation with token '{token}': {e}"
            )
            raise PasswordResetError("Failed to reset password")

    async def revoke_all_tokens(self, user_id: int) -> None:
        """
        Revoke all refresh tokens associated with a user.

        Args:
            user_id (int): The ID of the user whose tokens are to be revoked.

        Raises:
            RedisOperationError: If interacting with Redis fails.
        """
        try:
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False,
                )
            )
            tokens_to_revoke = result.scalars().all()
            for token in tokens_to_revoke:
                token.revoked = True
                self.db.add(token)
            await self.db.commit()

            # Optionally, add all tokens to Redis blacklist
            for token in tokens_to_revoke:
                await self.revoke_token(token.token)

            logger.info(f"All tokens revoked for user ID '{user_id}'.")
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                f"Database error during token revocation for user ID '{user_id}': {e}"
            )
            raise RedisOperationError("Failed to revoke tokens due to a database error")
        except Exception as e:
            logger.error(f"Error during token revocation for user ID '{user_id}': {e}")
            raise RedisOperationError("Failed to revoke tokens")

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Refresh the access token using a valid refresh token.

        Args:
            refresh_token (str): The refresh token provided by the user.

        Returns:
            Token: A new access token and refresh token.

        Raises:
            InvalidCredentialsError: If the refresh token is invalid or revoked.
        """
        try:
            # Check if the refresh token is blacklisted
            is_blacklisted = await self.is_token_blacklisted(refresh_token)
            if is_blacklisted:
                logger.warning(f"Refresh token '{refresh_token}' is blacklisted.")
                raise InvalidCredentialsError("Invalid refresh token.")

            # Retrieve the refresh token from the database
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.token == refresh_token,
                    RefreshToken.expires_at > datetime.utcnow(),
                    RefreshToken.revoked == False,
                )
            )
            token_entry = result.scalars().first()
            if not token_entry:
                logger.warning(f"Invalid or expired refresh token: '{refresh_token}'.")
                raise InvalidCredentialsError("Invalid or expired refresh token.")

            # Retrieve the associated user
            user = await self.db.get(DBUser, token_entry.user_id)
            if not user:
                logger.error(
                    f"User ID '{token_entry.user_id}' not found for refresh token '{refresh_token}'."
                )
                raise InvalidCredentialsError("Invalid refresh token.")

            user_in_db = UserInDB(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                disabled=user.disabled,
                mfa_enabled=user.mfa_enabled,
                mfa_secret=user.mfa_secret,
                wallet_address=user.wallet_address,
                profile_settings=user.profile_settings,
                roles=(
                    user.roles
                    if isinstance(user.roles, list)
                    else user.roles.split(",")
                ),
                portfolios=user.portfolios,
                refresh_tokens=user.refresh_tokens,
                sessions=user.sessions,
            )

            # Generate new tokens
            new_tokens = await self.generate_tokens(user_in_db)

            # Revoke the old refresh token
            token_entry.revoked = True
            self.db.add(token_entry)
            await self.db.commit()

            # Add the old refresh token to Redis blacklist
            await self.revoke_token(refresh_token)

            logger.info(f"Access token refreshed for user '{user.username}'.")

            return new_tokens
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                f"Database error during token refresh with token '{refresh_token}': {e}"
            )
            raise InvalidCredentialsError(
                "Failed to refresh access token due to a database error"
            )
        except Exception as e:
            logger.error(
                f"Error during token refresh with token '{refresh_token}': {e}"
            )
            raise InvalidCredentialsError("Failed to refresh access token")

    async def validate_access_token(self, token: str) -> Optional[UserInDB]:
        """
        Validate an access token and retrieve the associated user.

        Args:
            token (str): The JWT access token to validate.

        Returns:
            Optional[UserInDB]: The authenticated user's data if the token is valid, None otherwise.

        Raises:
            InvalidCredentialsError: If the token is invalid or blacklisted.
        """
        try:
            # Decode the token to extract payload
            payload = self.decode_token(token)
            username = payload.username

            if not username:
                logger.warning("Token payload missing 'username' field.")
                raise InvalidCredentialsError("Invalid token")

            # Check if the token is blacklisted
            is_blacklisted = await self.is_token_blacklisted(token)
            if is_blacklisted:
                logger.warning("Access token is blacklisted.")
                raise InvalidCredentialsError("Invalid token")

            # Retrieve the user
            user = await self.get_user(username)
            if not user:
                logger.warning(f"User '{username}' not found for token validation.")
                raise InvalidCredentialsError("Invalid token")

            return user
        except JWTError as e:
            logger.error(f"JWTError during token validation: {e}")
            raise InvalidCredentialsError("Invalid token")
        except Exception as e:
            logger.error(f"Error during access token validation: {e}")
            raise InvalidCredentialsError("Invalid token")
