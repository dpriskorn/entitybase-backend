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
    USER_CREATION = "user_creation"
    USER_DELETION = "user_deletion"
    WATCHLIST_ENABLED = "watchlist_enabled"
    WATCHLIST_DISABLED = "watchlist_disabled"
    PREFERENCES_UPDATED = "preferences_updated"
