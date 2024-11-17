# tests/unit/test_refresh_token.py

from datetime import datetime, timedelta

import pytest

from src.zimbot.core.models.user import RefreshToken


def test_refresh_token_is_expired():
    token = RefreshToken(expires_at=datetime.utcnow() - timedelta(seconds=1))
    assert token.is_expired() == True


def test_refresh_token_not_expired():
    token = RefreshToken(expires_at=datetime.utcnow() + timedelta(days=1))
    assert token.is_expired() == False


def test_increment_issuance():
    token = RefreshToken(issuance_count=1)
    token.increment_issuance()
    assert token.issuance_count == 2
