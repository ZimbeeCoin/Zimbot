from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoomCreate(BaseModel):
    """Data required to create a room."""

    name: str
    description: Optional[str] = None


class RoomModel(BaseModel):
    """Representation of a room."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
