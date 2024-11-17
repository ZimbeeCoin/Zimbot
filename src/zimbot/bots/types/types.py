from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BotCreate(BaseModel):
    """Data required to create a bot."""

    name: str
    description: Optional[str] = None


class BotModel(BaseModel):
    """Representation of a bot."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
