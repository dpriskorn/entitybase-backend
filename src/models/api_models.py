from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import Response
from pydantic import BaseModel, ConfigDict, Field


class EditType(str, Enum):
    """Standardized edit type classifications for filtering"""

    LOCK_ADDED = "lock-added"
    LOCK_REMOVED = "lock-removed"
    SEMI_PROTECTION_ADDED = "semi-protection-added"
    SEMI_PROTECTION_REMOVED = "semi-protection-removed"
    MASS_PROTECTION_ADDED = "mass-protection-added"
    MASS_PROTECTION_REMOVED = "mass-protection-removed"
    ARCHIVE_ADDED = "archive-added"
    ARCHIVE_REMOVED = "archive-removed"
    BOT_IMPORT = "bot-import"
    BOT_CLEANUP = "bot-cleanup"
    BOT_MERGE = "bot-merge"
    BOT_SPLIT = "bot-split"
    MANUAL_CREATE = "manual-create"
    MANUAL_UPDATE = "manual-update"
    MANUAL_CORRECTION = "manual-correction"
    CLEANUP_2025 = "cleanup-2025"
    CLEANUP_LABELS = "cleanup-labels"
    CLEANUP_DESCRIPTIONS = "cleanup-descriptions"
    MIGRATION_INITIAL = "migration-initial"
    MIGRATION_BATCH = "migration-batch"
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    UNDELETE = "undelete"
    REDIRECT_CREATE = "redirect-create"
    REDIRECT_REVERT = "redirect-revert"
    UNSPECIFIED = ""


class EntityCreateRequest(BaseModel):
    id: str = Field(..., description="Entity ID (e.g., Q42)")
    type: str = Field(default="item", description="Entity type")
    labels: Optional[Dict[str, Dict[str, str]]] = None
    descriptions: Optional[Dict[str, Dict[str, str]]] = None
    claims: Optional[Dict[str, List]] = None
    aliases: Optional[Dict[str, List]] = None
    sitelinks: Optional[Dict[str, Any]] = None
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    is_semi_protected: bool = Field(default=False, description="Item is semi-protected")
    is_locked: bool = Field(default=False, description="Item is locked from edits")
    is_archived: bool = Field(default=False, description="Item is archived")
    is_dangling: bool = Field(
        default=False,
        description="Item has no maintaining WikiProject (computed by frontend)",
    )
    is_mass_edit_protected: bool = Field(
        default=False, description="Item is protected from mass edits"
    )
    is_not_autoconfirmed_user: bool = Field(
        default=False, description="User is not autoconfirmed (new/unconfirmed account)"
    )
    edit_summary: str = Field(default="", description="Edit summary for this change")
    editor: str = Field(default="", description="Editor who made this change")
    bot: bool = Field(default=False, description="Whether this was a bot edit")

    model_config = ConfigDict(extra="allow")

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class EntityResponse(BaseModel):
    id: str
    revision_id: int
    data: Dict[str, Any]
    is_semi_protected: bool = False
    is_locked: bool = False
    is_archived: bool = False
    is_dangling: bool = False
    is_mass_edit_protected: bool = False


class DeleteType(str, Enum):
    SOFT = "soft"
    HARD = "hard"


class EntityDeleteRequest(BaseModel):
    delete_type: DeleteType = Field(
        default=DeleteType.SOFT, description="Type of deletion"
    )
    is_locked: bool = Field(default=False, description="User has lock permission")
    edit_summary: str = Field(default="", description="Edit summary for deletion")
    editor: str = Field(default="", description="Editor who performed deletion")
    bot: bool = Field(default=False, description="Whether this was a bot edit")


class EntityDeleteResponse(BaseModel):
    id: str
    revision_id: int
    is_deleted: bool = Field(..., description="Whether entity is deleted")
    deletion_type: str = Field(..., description="Type of deletion performed")
    deletion_status: str = Field(
        ..., description="Status of deletion (soft_deleted/hard_deleted)"
    )


class EntityRedirectRequest(BaseModel):
    redirect_from_id: str = Field(
        ..., description="Source entity ID to be marked as redirect (e.g., Q59431323)"
    )
    redirect_to_id: str = Field(..., description="Target entity ID (e.g., Q42)")
    created_by: str = Field(
        default="rest-api", description="User or system creating redirect"
    )


class EntityRedirectResponse(BaseModel):
    redirect_from_id: str
    redirect_to_id: str
    created_at: str
    revision_id: int


class RedirectRevertRequest(BaseModel):
    revert_to_revision_id: int = Field(
        ..., description="Revision ID to revert to (e.g., 12340)"
    )
    revert_reason: str = Field(..., description="Reason for reverting redirect")
    created_by: str = Field(default="rest-api")


class StatementResponse(BaseModel):
    content_hash: int = Field(..., description="Statement hash")
    statement: Dict[str, Any] = Field(..., description="Full statement JSON")
    created_at: str = Field(..., description="Creation timestamp")


class StatementBatchRequest(BaseModel):
    hashes: list[int] = Field(..., description="List of statement hashes to fetch")


class StatementBatchResponse(BaseModel):
    statements: list[StatementResponse] = Field(..., description="List of statements")
    not_found: list[int] = Field(
        default_factory=list,
        description="Hashes that were not found",
    )


class PropertyListResponse(BaseModel):
    properties: list[str] = Field(
        default_factory=list, description="List of unique property IDs"
    )


class PropertyCountsResponse(BaseModel):
    property_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Dict mapping property ID -> statement count",
    )


class PropertyHashesResponse(BaseModel):
    property_hashes: list[int] = Field(
        default_factory=list,
        description="List of statement hashes for specified properties",
    )


# class MostUsedStatementsRequest(BaseModel):
#     limit: int = Field(
#         default=100,
#         ge=1,
#         le=10000,
#         description="Maximum number of statements to return (1-10000, default 100)",
#     )
#     min_ref_count: int = Field(
#         default=1,
#         ge=0,
#         description="Minimum ref_count threshold (default 1)",
#     )


class MostUsedStatementsResponse(BaseModel):
    statements: list[int] = Field(
        default_factory=list,
        description="List of statement hashes sorted by ref_count DESC",
    )


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


# class EntityListResponse(BaseModel):
#     entities: list[dict[str, Any]] = Field(
#         description="List of entities with their metadata"
#     )
#     count: int = Field(description="Total number of entities returned")


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str


class HealthCheckResponse(BaseModel):
    status: str
    s3: str
    vitess: str


class StatementHashResult(BaseModel):
    statements: list[int] = Field(
        default_factory=list,
        description="List of statement hashes (rapidhash of each statement)",
    )
    properties: list[str] = Field(
        default_factory=list,
        description="Sorted list of unique property IDs",
    )
    property_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Dict mapping property ID -> count of statements",
    )
    full_statements: list[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of full statement dicts (parallel with hashes)",
    )
