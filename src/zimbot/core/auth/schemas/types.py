# src/zimbot/core/auth/schemas/types.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class RefreshTokenData(BaseModel):
    token: str
    expires_at: datetime
    revoked: bool

    class Config:
        orm_mode = True


class UserSessionData(BaseModel):
    action: str
    timestamp: datetime

    class Config:
        orm_mode = True


class PortfolioAssetData(BaseModel):
    symbol: str
    quantity: float
    average_price: Optional[float] = None
    current_price: Optional[float] = None

    class Config:
        orm_mode = True


class PortfolioData(BaseModel):
    name: str
    created_at: datetime
    last_synced: Optional[datetime] = None
    assets: List[PortfolioAssetData] = []

    class Config:
        orm_mode = True


class UserInDB(BaseModel):
    id: int
    username: str = Field(..., max_length=150)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    hashed_password: str
    disabled: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = Field(None, max_length=32)
    wallet_address: Optional[str] = Field(None, max_length=42)
    profile_settings: Optional[dict] = None
    roles: List[str] = Field(default_factory=lambda: ["user"])
    portfolios: List[PortfolioData] = []
    refresh_tokens: List[RefreshTokenData] = []
    sessions: List[UserSessionData] = []

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: Optional[List[str]] = []


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(..., max_length=150)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8)
    wallet_address: Optional[str] = Field(None, max_length=42)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    wallet_address: Optional[str] = Field(None, max_length=42)
    profile_settings: Optional[dict] = None
    roles: Optional[List[str]] = None  # Allow role updates if necessary


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class MFASetupResponse(BaseModel):
    mfa_secret: str
    otp_uri: str  # URI for QR code generation
