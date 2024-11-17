# tests/unit/core/models/test_models.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.zimbot.core.models.user import Base, Role, User, UserRole


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_create_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        mfa_enabled=True,
        mfa_secret="MFASECRET123456",
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
    )
    db_session.add(user)
    db_session.commit()
    retrieved_user = db_session.query(User).filter_by(username="testuser").first()
    assert retrieved_user.email == "test@example.com"
