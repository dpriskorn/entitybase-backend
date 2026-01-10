from enum import Enum
from typing import Any, Dict

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


class EntityCreateRequest(BaseModel):
    id: str = Field(..., description="Entity ID (e.g., Q42)")
    type: str = Field(default="item", description="Entity type")
    labels: Dict[str, Dict[str, str]] = {}
    descriptions: Dict[str, Dict[str, str]] = {}
    claims: Dict[str, Any] = {}
    aliases: Dict[str, Any] = {}
    sitelinks: Dict[str, Any] = {}
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
    schema_version: str = Field(..., description="Schema version")
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


class MostUsedStatementsRequest(BaseModel):
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


class EntityListResponse(BaseModel):
    entities: list[dict[str, Any]] = Field(
        description="List of entities with their metadata"
    )
    count: int = Field(description="Total number of entities returned")


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str


class HealthResponse(BaseModel):
    status: str


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


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""

    type: str = Field(default="item", description="Entity type")
    labels: Dict[str, Dict[str, str]] = {}
    descriptions: Dict[str, Dict[str, str]] = {}
    claims: Dict[str, Any] = {}
    aliases: Dict[str, Any] = {}
    sitelinks: Dict[str, Any] = {}
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

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class Backlink(BaseModel):
    """Model representing a backlink from one entity to another."""

    entity_id: str = Field(description="Entity ID that references the target")
    property_id: str = Field(description="Property used in the reference")
    rank: str = Field(description="Rank of the statement (normal/preferred/deprecated)")


class BacklinksResponse(BaseModel):
    """Response model for backlinks API."""

    backlinks: list[Backlink] = Field(description="List of backlinks")
    limit: int = Field(description="Requested limit")
    offset: int = Field(description="Requested offset")


class MetadataLoadResponse(BaseModel):
    """Response model for metadata loading operations."""

    results: dict[str, bool] = Field(
        description="Dictionary mapping entity_id to success status"
    )


class EntityMetadata(BaseModel):
    """Model for entity metadata."""

    id: str
    labels: dict[str, dict[str, str]] = Field(default_factory=dict)
    descriptions: dict[str, dict[str, str]] = Field(default_factory=dict)


class EntityMetadataBatchResponse(BaseModel):
    """Response model for batch entity metadata fetching."""

    metadata: dict[str, EntityMetadata | None] = Field(
        description="Dictionary mapping entity_id to metadata or None"
    )


class RedirectBatchResponse(BaseModel):
    """Response model for batch entity redirects fetching."""

    redirects: dict[str, list[str]] = Field(
        description="Dictionary mapping entity_id to list of redirect titles"
    )


class WikibasePredicates(BaseModel):
    """Model for Wikibase predicate URIs for a property."""

    direct: str = Field(description="Direct property predicate")
    statement: str = Field(description="Statement property predicate")
    statement_value: str = Field(description="Statement value property predicate")
    qualifier: str = Field(description="Qualifier property predicate")
    reference: str = Field(description="Reference property predicate")
    statement_value_node: str = Field(description="Statement value node predicate")


class EntityLabels(BaseModel):
    """Model for entity labels."""

    labels: dict[str, str] = Field(default_factory=dict)


class EntityDescriptions(BaseModel):
    """Model for entity descriptions."""

    descriptions: dict[str, str] = Field(default_factory=dict)


class EntityAliases(BaseModel):
    """Model for entity aliases."""

    aliases: dict[str, list[str]] = Field(default_factory=dict)


class PropertyCounts(BaseModel):
    """Model for property statement counts."""

    counts: dict[str, int] = Field(
        description="Dictionary mapping property ID to statement count"
    )


class WorkerHealthCheck(BaseModel):
    """Model for worker health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    worker_id: str = Field(description="Unique worker identifier")
    range_status: dict[str, Any] = Field(
        description="Current ID range allocation status"
    )


class EntityRevisionResponse(BaseModel):
    """Model for entity revision response."""

    entity_id: str = Field(description="Entity ID")
    revision_id: int = Field(description="Revision ID")
    data: dict[str, Any] = Field(description="Revision data")


class DeduplicationStats(BaseModel):
    """Model for deduplication cache statistics."""

    hits: int = Field(description="Number of cache hits")
    misses: int = Field(description="Number of cache misses")
    size: int = Field(description="Current cache size")
    collision_rate: float = Field(description="Collision rate percentage")


class FullRevisionData(BaseModel):
    """Model for full revision data from database."""

    revision_id: int = Field(description="Revision ID")
    statements: list[int] = Field(description="List of statement hashes")
    properties: list[str] = Field(description="List of unique properties")
    property_counts: dict[str, int] = Field(description="Property counts")


class ProtectionInfo(BaseModel):
    """Model for entity protection information."""

    is_semi_protected: bool = Field(description="Whether entity is semi-protected")
    is_locked: bool = Field(description="Whether entity is locked")
    is_archived: bool = Field(description="Whether entity is archived")
    is_dangling: bool = Field(description="Whether entity is dangling")
    is_mass_edit_protected: bool = Field(
        description="Whether entity is mass edit protected"
    )
