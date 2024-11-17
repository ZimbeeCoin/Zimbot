# tests/integration/api/test_auth_endpoint.py

import pytest
from httpx import AsyncClient

from zimbot.core.auth.schemas.types import UserInDB
from zimbot.core.auth.services.auth_service import AuthService
from zimbot.core.integrations.exceptions import InvalidCredentialsError
from zimbot.main import app


@pytest.fixture
async def auth_service_mock(monkeypatch):
    class MockAuthService(AuthService):
        async def initialize(self, redis, db):
            pass

        async def authenticate_user(self, username: str, password: str) -> UserInDB:
            if username == "johndoe" and password == "secret":
                return UserInDB(
                    username="johndoe",
                    email="johndoe@example.com",
                    full_name="John Doe",
                    hashed_password="hashedpassword",
                    disabled=False,
                    mfa_enabled=False,
                    roles=["user"],
                    refresh_tokens=[],
                )
            else:
                raise InvalidCredentialsError("Invalid username or password")

        async def generate_tokens(self, user: UserInDB) -> dict:
            return {
                "access_token": "access.jwt.token",
                "refresh_token": "refresh.jwt.token",
                "token_type": "bearer",
            }

    mock_service = MockAuthService()
    monkeypatch.setattr("src.api.auth.AuthService", lambda: mock_service)
    return mock_service


@pytest.mark.asyncio
async def test_login_success(auth_service_mock):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/token", data={"username": "johndoe", "password": "secret"}
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


@pytest.mark.asyncio
async def test_login_failure(auth_service_mock):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/token",
            data={"username": "johndoe", "password": "wrongpassword"},
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
