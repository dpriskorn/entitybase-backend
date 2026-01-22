"""Change type enum for entity changes."""

from enum import Enum


class ChangeType(str, Enum):
    """Enum for different types of entity changes."""

    CREATION = "creation"
    EDIT = "edit"
    REDIRECT = "redirect"
    UNREDIRECT = "unredirect"
    ARCHIVAL = "archival"
    UNARCHIVAL = "unarchival"
    LOCK = "lock"
    UNLOCK = "unlock"
    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"
    REVERT = "revert"
