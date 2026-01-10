from enum import Enum

from pydantic import BaseModel


class EditType(Enum):
    """Enumeration of different types of edits that can be made to entities."""

    LOCK_ADDED = "lock-added"
    LOCK_REMOVED = "lock-removed"
    SEMI_PROTECTION_ADDED = "semi-protection-added"
    SEMI_PROTECTION_REMOVED = "semi-protection-removed"
    MASS_PROTECTION_ADDED = "mass-protection-added"
    MASS_PROTECTION_REMOVED = "mass-protection-removed"
    UNSPECIFIED = "unspecified"
    MANUAL_CREATE = "manual-create"
    MANUAL_UPDATE = "manual-update"
    MANUAL_CORRECTION = "manual-correction"
    REDIRECT_CREATE = "redirect-create"
    REDIRECT_REVERT = "redirect-revert"
    ARCHIVE_ADDED = "archive-added"
    ARCHIVE_REMOVED = "archive-removed"
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    BOT_IMPORT = "bot-import"
    BOT_CLEANUP = "bot-cleanup"
    BOT_MERGE = "bot-merge"
    BOT_SPLIT = "bot-split"
    CLEANUP_2025 = "cleanup-2025"
    CLEANUP_LABELS = "cleanup-labels"
    CLEANUP_DESCRIPTIONS = "cleanup-descriptions"
    MIGRATION_INITIAL = "migration-initial"
    MIGRATION_BATCH = "migration-batch"
    SOFT = "soft-delete"
    HARD = "hard-delete"
    UNDELETE = "undelete"


class DeleteType(str, Enum):
    SOFT = "soft"
    HARD = "hard"


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str
