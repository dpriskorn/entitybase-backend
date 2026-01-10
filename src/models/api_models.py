from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class EditType(Enum):
    """Enumeration of different types of edits that can be made to entities."""

    UNSPECIFIED = "unspecified"
    MANUAL_CREATE = "manual-create"
    MANUAL_UPDATE = "manual-update"
    MANUAL_CORRECTION = "manual-correction"
    REDIRECT_CREATE = "redirect-create"
    REDIRECT_REVERT = "redirect-revert"
    ARCHIVE_ADDED = "archive-added"
    ARCHIVE_REMOVED = "archive-removed"
    LOCK_ADDED = "lock-added"
    LOCK_REMOVED = "lock-removed"
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    BOT_IMPORT = "bot-import"
    BOT_CLEANUP = "bot-cleanup"
    BOT_MERGE = "bot-merge"
    BOT_SPLIT = "bot-split"
    MIGRATION_INITIAL = "migration-initial"
    MIGRATION_BATCH = "migration-batch"


class DeleteType(Enum):
    """Enumeration of different types of deletions."""

    SOFT = "soft-delete"
    HARD = "hard-delete"


class ItemCreateRequest(BaseModel):
    """Request model for creating a new Wikibase item."""

    id: str = ""
    type: str = Field(default="item", description="Entity type (must be 'item')")
    labels: Dict[str, Dict[str, str]] | None = None
    descriptions: Dict[str, Dict[str, str]] | None = None
    claims: Dict[str, Any] | None = None
    aliases: Dict[str, Any] | None = None
    sitelinks: Dict[str, Any] | None = None
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


class ItemUpdateRequest(BaseModel):
    """Request model for updating an existing Wikibase item."""

    type: str = Field(default="item", description="Entity type (must be 'item')")
    labels: Dict[str, Dict[str, str]] | None = None
    descriptions: Dict[str, Dict[str, str]] | None = None
    claims: Dict[str, Any] | None = None
    aliases: Dict[str, Any] | None = None
    sitelinks: Dict[str, Any] | None = None
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


class EntityCreateRequest(BaseModel):
    """Request model for creating a new Wikibase property."""

    id: str = ""
    type: str = Field(
        default="property", description="Entity type (must be 'property')"
    )
    labels: Dict[str, Dict[str, str]] | None = None
    descriptions: Dict[str, Dict[str, str]] | None = None
    claims: Dict[str, Any] | None = None
    aliases: Dict[str, Any] | None = None
    sitelinks: Dict[str, Any] | None = None
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    is_semi_protected: bool = Field(
        default=False, description="Property is semi-protected"
    )
    is_locked: bool = Field(default=False, description="Property is locked from edits")
    is_archived: bool = Field(default=False, description="Property is archived")
    is_dangling: bool = Field(
        default=False,
        description="Property has no maintaining WikiProject (computed by frontend)",
    )
    is_mass_edit_protected: bool = Field(
        default=False, description="Property is protected from mass edits"
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
    """Response model for entity operations."""

    id: str
    revision_id: int
    data: Dict[str, Any]
    is_semi_protected: bool
    is_locked: bool
    is_archived: bool
    is_dangling: bool
    is_mass_edit_protected: bool


ItemResponse = EntityResponse


class CleanupOrphanedRequest(BaseModel):
    """Request model for cleanup orphaned entities."""

    older_than_days: int = Field(default=180, description="Minimum age in days")
    limit: int = Field(default=1000, description="Maximum statements to cleanup")


class CleanupOrphanedResponse(BaseModel):
    """Response model for cleanup orphaned entities."""

    cleaned_count: int = Field(description="Number of statements cleaned")
    failed_count: int = Field(description="Number of statements that failed to clean")
    errors: list[str] = Field(
        default_factory=list, description="List of error messages"
    )


class EntityDeleteRequest(BaseModel):
    """Request model for deleting an entity."""

    delete_type: DeleteType = Field(description="Type of deletion")
    edit_summary: str = Field(default="", description="Edit summary")
    editor: str = Field(default="", description="Editor who performed the deletion")
    bot: bool = Field(default=False, description="Whether the editor is a bot")


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""

    type: str = Field(default="item", description="Entity type")
    labels: Dict[str, Dict[str, str]] | None = None
    descriptions: Dict[str, Dict[str, str]] | None = None
    claims: Dict[str, Any] | None = None
    aliases: Dict[str, Any] | None = None
    sitelinks: Dict[str, Any] | None = None
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


class EntityDeleteResponse(BaseModel):
    """Response model for entity deletion."""

    pass


class EntityListResponse(BaseModel):
    """Response model for entity list."""

    pass


class EntityRedirectResponse(BaseModel):
    """Response model for entity redirect."""

    pass


class EntityRedirectRequest(BaseModel):
    """Request model for entity redirect."""

    pass


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    pass


class MostUsedStatementsResponse(BaseModel):
    """Response model for most used statements."""

    pass


class PropertyCountsResponse(BaseModel):
    """Response model for property counts."""

    pass


class PropertyHashesResponse(BaseModel):
    """Response model for property hashes."""

    pass


class PropertyListResponse(BaseModel):
    """Response model for property list."""

    pass


class RedirectRevertRequest(BaseModel):
    """Request model for redirect revert."""

    pass


class RevisionMetadata(BaseModel):
    """Metadata for revision."""

    pass


class StatementBatchRequest(BaseModel):
    """Request model for statement batch."""

    pass


class StatementBatchResponse(BaseModel):
    """Response model for statement batch."""

    pass


class StatementResponse(BaseModel):
    """Response model for statement."""

    pass


class TtlResponse(BaseModel):
    """Response model for TTL."""

    pass


class StatementHashResult(BaseModel):
    """Result of statement hashing."""

    statements: list[int]
    properties: list[str]
    property_counts: dict[str, int]
