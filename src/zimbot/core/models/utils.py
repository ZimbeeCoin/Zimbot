# src/zimbot/core/models/utils.py

import functools
import json
import logging
import os
import re
import time
import uuid
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from logging import handlers  # Moved this import to the top
from typing import Any, Deque, Dict, List, Optional, Sequence, TypeVar

import bcrypt
from cryptography.fernet import Fernet

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Security Enhancements

# Ensure ENCRYPTION_KEY is securely managed in environment variables.
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if ENCRYPTION_KEY is None:
    raise OSError("ENCRYPTION_KEY environment variable not set.")
fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_data(data: str) -> str:
    """
    Encrypt a string using Fernet.

    Args:
        data (str): The plaintext data to encrypt.

    Returns:
        str: The encrypted data, base64 encoded.
    """
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(data: str) -> str:
    """
    Decrypt a string using Fernet.

    Args:
        data (str): The encrypted data to decrypt.

    Returns:
        str: The decrypted plaintext data.
    """
    return fernet.decrypt(data.encode()).decode()


def hash_password(password: str) -> str:
    """
    Hash a password for storing.

    Args:
        password (str): The plaintext password.

    Returns:
        str: The hashed password.
    """
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


def check_password(password: str, hashed_password: str) -> bool:
    """
    Check a password against an existing hash.

    Args:
        password (str): The plaintext password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def generate_uuid() -> str:
    """
    Generate a unique UUID string.

    Returns:
        str: A unique UUID string.
    """
    return str(uuid.uuid4())


# Date and Time Utilities


def current_time_utc() -> datetime:
    """
    Get the current UTC time.

    Returns:
        datetime: The current time in UTC.
    """
    return datetime.now(timezone.utc)


def time_diff_in_seconds(start_time: datetime, end_time: datetime) -> int:
    """
    Calculate the difference in seconds between two datetime objects.

    Args:
        start_time (datetime): The starting datetime.
        end_time (datetime): The ending datetime.

    Returns:
        int: The difference in seconds.
    """
    delta = end_time - start_time
    return int(delta.total_seconds())


def default_expiration(days: int = 7) -> datetime:
    """
    Calculate the default expiration datetime.

    Args:
        days (int): Number of days until expiration.

    Returns:
        datetime: Datetime object representing expiration time.
    """
    return datetime.utcnow() + timedelta(days=days)


# JSON Utilities


def to_json(data: Any) -> str:
    """
    Serialize data to a JSON-formatted string.

    Args:
        data (Any): The data to serialize.

    Returns:
        str: JSON-formatted string.
    """
    return json.dumps(data, default=str)


def from_json(data: str) -> Any:
    """
    Deserialize data from a JSON-formatted string.

    Args:
        data (str): JSON-formatted string.

    Returns:
        Any: The deserialized data.
    """
    return json.loads(data)


# Data Validation Utilities


def is_valid_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    email_regex = r"(^[\w\.\-]+@[\w\.\-]+\.\w+$)"
    return bool(re.match(email_regex, email))


def is_valid_phone(phone: str) -> bool:
    """
    Validate a phone number format (simplified E.164).

    Args:
        phone (str): The phone number to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    phone_regex = r"^\+?[1-9]\d{1,14}$"
    return bool(re.match(phone_regex, phone))


# Pagination Utility


def paginate(items: Sequence[T], page: int, page_size: int) -> List[T]:
    """
    Paginate a list of items.

    Args:
        items (Sequence[T]): The list or sequence of items to paginate.
        page (int): The page number (1-based).
        page_size (int): The number of items per page.

    Returns:
        List[T]: A paginated sublist of items.
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10  # Default page size
    start = (page - 1) * page_size
    end = start + page_size
    return list(items[start:end])


# Retry Decorator


def retry(exception_to_check, tries=3, delay=1, backoff=2):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exception_to_check (Exception or tuple): The exception to check.
        tries (int): Number of attempts.
        delay (int): Initial delay between retries in seconds.
        backoff (int): Backoff multiplier.

    Returns:
        function: Decorated function with retry logic.
    """

    def deco_retry(f):

        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay

            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    logging.warning(f"Retrying due to {e}, tries left: {mtries - 1}")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry


# Exception Handling Utilities


class CustomError(Exception):
    """Base class for custom exceptions."""

    pass


class ValidationError(CustomError):
    """Exception raised for validation errors."""

    pass


def handle_exception(e: Exception) -> None:
    """
    Handle exceptions in a standardized way.

    Args:
        e (Exception): The exception to handle.
    """
    logging.error(f"An error occurred: {str(e)}")
    # Additional handling logic can be added here


# Logging Utility


def setup_logging(log_file: str, level=logging.INFO) -> None:
    """
    Set up logging for the application.

    Args:
        log_file (str): The path to the log file.
        level (int): Logging level.
    """
    handler = handlers.RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
    logging.basicConfig(
        handlers=[handler],
        level=level,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )


# General Utilities


def chunk_list(data_list: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks.

    Args:
        data_list (List[T]): The list to split.
        chunk_size (int): The size of each chunk.

    Returns:
        List[List[T]]: A list of chunks.
    """
    return [data_list[i : i + chunk_size] for i in range(0, len(data_list), chunk_size)]
