"""User roles for access control."""

from enum import Enum


class UserRole(str, Enum):
    """User roles for access control."""

    ADMIN = "admin"
    DEFAULT = "default"

    @classmethod
    def values(cls) -> list[str]:
        """Return list of valid role values."""
        return [role.value for role in cls]
