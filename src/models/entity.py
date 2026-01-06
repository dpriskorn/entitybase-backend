from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EditType(str, Enum):
    """Standardized edit type classifications for filtering"""

    # Protection management
    LOCK_ADDED = "lock-added"
    LOCK_REMOVED = "lock-removed"
    SEMI_PROTECTION_ADDED = "semi-protection-added"
    SEMI_PROTECTION_REMOVED = "semi-protection-removed"
    ARCHIVE_ADDED = "archive-added"
    ARCHIVE_REMOVED = "archive-removed"

    # Mass edit classifications
    BOT_IMPORT = "bot-import"
    BOT_CLEANUP = "bot-cleanup"
    BOT_MERGE = "bot-merge"
    BOT_SPLIT = "bot-split"

    # Manual edit classifications
    MANUAL_CREATE = "manual-create"
    MANUAL_UPDATE = "manual-update"
    MANUAL_CORRECTION = "manual-correction"

    # Cleanup campaigns
    CLEANUP_2025 = "cleanup-2025"
    CLEANUP_LABELS = "cleanup-labels"
    CLEANUP_DESCRIPTIONS = "cleanup-descriptions"

    # Migration operations
    MIGRATION_INITIAL = "migration-initial"
    MIGRATION_BATCH = "migration-batch"

    # Deletion operations
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    UNDELETE = "undelete"

    # Redirect operations
    REDIRECT_CREATE = "redirect-create"
    REDIRECT_REVERT = "redirect-revert"

    # Default
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
    edit_type: str = Field(
        default="",
        description="Text classification of edit type (e.g., 'bot-import', 'cleanup')",
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

    model_config = ConfigDict(extra="allow")

    @property
    def data(self) -> Dict[str, Any]:
        """Return entity as dict for compatibility with existing code"""
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


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str


class HealthCheckResponse(BaseModel):
    status: str
    s3: str
    vitess: str


class DeleteType(str, Enum):
    """Deletion type classification"""

    SOFT = "soft"
    HARD = "hard"


class EntityDeleteRequest(BaseModel):
    delete_type: DeleteType = Field(
        default=DeleteType.SOFT, description="Type of deletion"
    )


class EntityDeleteResponse(BaseModel):
    id: str
    revision_id: int
    delete_type: DeleteType
    is_deleted: bool


class EntityRedirectRequest(BaseModel):
    redirect_from_id: str = Field(
        ..., description="Source entity ID to be marked as redirect (e.g., Q59431323)"
    )
    redirect_to_id: str = Field(..., description="Target entity ID (e.g., Q42)")
    created_by: str = Field(
        default="entity-api", description="User or system creating redirect"
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
    created_by: str = Field(default="entity-api")


class StatementHashResult(BaseModel):
    """Result of hashing entity statements for deduplication"""

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


class StatementBatchRequest(BaseModel):
    """Request to fetch multiple statements by hash"""

    hashes: list[int] = Field(..., description="List of statement hashes to fetch")


class StatementResponse(BaseModel):
    """Response for a single statement"""

    content_hash: int = Field(..., description="Statement hash")
    statement: Dict[str, Any] = Field(..., description="Full statement JSON")
    created_at: str = Field(..., description="Creation timestamp")


class StatementBatchResponse(BaseModel):
    """Response for batch statement fetch"""

    statements: list[StatementResponse] = Field(..., description="List of statements")
    not_found: list[int] = Field(
        default_factory=list,
        description="Hashes that were not found",
    )


class PropertyListResponse(BaseModel):
    """Response for property list endpoint"""

    properties: list[str] = Field(
        default_factory=list, description="List of unique property IDs"
    )


class PropertyCountsResponse(BaseModel):
    """Response for property counts endpoint"""

    property_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Dict mapping property ID -> statement count",
    )


class PropertyHashesResponse(BaseModel):
    """Response for property-specific hashes endpoint"""

    property_hashes: list[int] = Field(
        default_factory=list,
        description="List of statement hashes for specified properties",
    )


class MostUsedStatementsRequest(BaseModel):
    """Request parameters for most-used statements endpoint"""

    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of statements to return (1-10000, default 100)",
    )
    min_ref_count: int = Field(
        default=1,
        ge=0,
        description="Minimum ref_count threshold (default 1)",
    )


class MostUsedStatementsResponse(BaseModel):
    """Response for most-used statements endpoint"""

    statements: list[int] = Field(
        default_factory=list,
        description="List of statement hashes sorted by ref_count DESC",
    )


class CleanupOrphanedRequest(BaseModel):
    """Request parameters for orphaned statement cleanup"""

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
    """Response for orphaned statement cleanup"""

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


class EntityListResponse(BaseModel):
    """Response model for entity listing endpoints"""

    entities: list[dict[str, Any]] = Field(
        description="List of entities with their metadata"
    )
    count: int = Field(description="Total number of entities returned")
