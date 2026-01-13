from typing import Dict, Any, List

from pydantic import BaseModel, Field

from models.rest_api.response.entity.wikibase_json import EntityMetadata


class EntityHistoryEntry(BaseModel):
    """Response model for a single entity history entry."""

    revision_id: int
    created_at: str | None
    created_by: str | None
    edit_summary: str | None
    editor: str | None
    edit_type: str | None
    is_mass_edit: bool


class EntityResponse(BaseModel):
    """Response model for entity data."""

    id: str
    revision_id: int
    data: Dict[str, Any]
    is_semi_protected: bool = False
    is_locked: bool = False
    is_archived: bool = False
    is_dangling: bool = False
    is_mass_edit_protected: bool = False


class WikibaseEntityResponse(BaseModel):
    """Response model for Wikibase REST API entity endpoints."""

    id: str
    type: str  # "item", "property", "lexeme"
    labels: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    descriptions: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    aliases: Dict[str, List[Dict[str, str]]] = Field(default_factory=dict)
    claims: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    sitelinks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class EntityDeleteResponse(BaseModel):
    """Response model for entity deletion."""

    id: str
    revision_id: int
    is_deleted: bool = Field(..., description="Whether entity is deleted")
    deletion_type: str = Field(..., description="Type of deletion performed")
    deletion_status: str = Field(
        ..., description="Status of deletion (soft_deleted/hard_deleted)"
    )


class EntityRedirectResponse(BaseModel):
    """Response model for entity redirect creation."""

    redirect_from_id: str
    redirect_to_id: str
    created_at: str
    revision_id: int


class EntityListResponse(BaseModel):
    """Response model for entity list queries."""

    entities: list[dict[str, Any]] = Field(
        description="List of entities with their metadata"
    )
    count: int = Field(description="Total number of entities returned")


class EntityMetadataBatchResponse(BaseModel):
    """Response model for batch entity metadata fetching."""

    metadata: dict[str, EntityMetadata | None] = Field(
        description="Dictionary mapping entity_id to metadata or None"
    )


class EntityRevisionResponse(BaseModel):
    """Model for entity revision response."""

    entity_id: str = Field(description="Entity ID")
    revision_id: int = Field(description="Revision ID")
    data: dict[str, Any] = Field(description="Revision data")


class ProtectionResponse(BaseModel):
    """Model for entity protection information."""

    is_semi_protected: bool = Field(description="Whether entity is semi-protected")
    is_locked: bool = Field(description="Whether entity is locked")
    is_archived: bool = Field(description="Whether entity is archived")
    is_dangling: bool = Field(description="Whether entity is dangling")
    is_mass_edit_protected: bool = Field(
        description="Whether entity is mass edit protected"
    )


class EntityJsonImportResponse(BaseModel):
    """Response model for JSONL entity import operations."""

    processed_count: int = Field(description="Number of lines processed")
    imported_count: int = Field(description="Number of entities successfully imported")
    failed_count: int = Field(description="Number of entities that failed to import")
    error_log_path: str = Field(
        description="Path to error log file for malformed lines"
    )
