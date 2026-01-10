from enum import Enum

from pydantic import BaseModel, Field

from fastapi import Response


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


class TtlResponse(Response):
    def __init__(self, content: str):
        super().__init__(
            content=content,
            media_type="text/turtle",
        )


class CleanupOrphanedRequest(BaseModel):
    older_than_days: int = Field(
        default=180,
        ge=1,
        le=365,
        description="Minimum age in days before cleanup (default 180)",
    )
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of statements to cleanup (default 1000)",
    )


class CleanupOrphanedResponse(BaseModel):
    cleaned_count: int = Field(
        ...,
        description="Number of statements cleaned up from S3 and Vitess",
    )
    failed_count: int = Field(
        default=0,
        description="Number of statements that failed to clean up",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages for failed cleanups",
    )


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str
