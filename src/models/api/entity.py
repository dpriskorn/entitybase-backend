from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .misc import DeleteType, EditType


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


class EntityListResponse(BaseModel):
    entities: list[dict[str, Any]] = Field(
        description="List of entities with their metadata"
    )
    count: int = Field(description="Total number of entities returned")


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


class EntityLabels(BaseModel):
    """Model for entity labels."""

    labels: dict[str, str] = Field(default_factory=dict)


class EntityDescriptions(BaseModel):
    """Model for entity descriptions."""

    descriptions: dict[str, str] = Field(default_factory=dict)


class EntityAliases(BaseModel):
    """Model for entity aliases."""

    aliases: dict[str, list[str]] = Field(default_factory=dict)


class EntityRevisionResponse(BaseModel):
    """Model for entity revision response."""

    entity_id: str = Field(description="Entity ID")
    revision_id: int = Field(description="Revision ID")
    data: dict[str, Any] = Field(description="Revision data")


class ProtectionInfo(BaseModel):
    """Model for entity protection information."""

    is_semi_protected: bool = Field(description="Whether entity is semi-protected")
    is_locked: bool = Field(description="Whether entity is locked")
    is_archived: bool = Field(description="Whether entity is archived")
    is_dangling: bool = Field(description="Whether entity is dangling")
    is_mass_edit_protected: bool = Field(
        description="Whether entity is mass edit protected"
    )


class EntityJsonImportRequest(BaseModel):
    """Request model for importing entities from Wikidata JSONL dump."""

    jsonl_file_path: str = Field(
        ..., description="Path to JSONL file containing Wikidata entities"
    )
    start_line: int = Field(
        default=2, description="Starting line number (default 2, skips header)"
    )
    end_line: Optional[int] = Field(
        default=None, description="Ending line number (None = to end)"
    )
    overwrite_existing: bool = Field(
        default=False, description="Whether to overwrite existing entities"
    )
    worker_id: Optional[str] = Field(
        default=None, description="Worker identifier for logging"
    )


class EntityJsonImportResponse(BaseModel):
    """Response model for JSONL entity import operations."""

    processed_count: int = Field(description="Number of lines processed")
    imported_count: int = Field(description="Number of entities successfully imported")
    failed_count: int = Field(description="Number of entities that failed to import")
    error_log_path: str = Field(
        description="Path to error log file for malformed lines"
    )
