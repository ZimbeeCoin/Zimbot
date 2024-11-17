# src/zimbot/core/models/role.py

from __future__ import annotations  # Enable forward references for type hints

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User  # Type-only import to prevent circular imports


class Role(Base):
    """
    Represents a role that can be assigned to users.
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    permissions: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    hierarchy_level: Mapped[int] = mapped_column(Integer, nullable=True, default=1)

    users: Mapped[list[User]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("name", name="uq_role_name"),)

    # Utility Method

    def has_permission(self, permission: str) -> bool:
        """
        Check if the role includes a specific permission.

        Args:
            permission (str): The permission to check.

        Returns:
            bool: True if the role has the permission, False otherwise.
        """
        return permission in self.permissions.get("allowed", [])

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}', hierarchy_level={self.hierarchy_level})>"
