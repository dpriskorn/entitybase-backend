"""Entity response models for REST API."""

from typing import Any, Dict

from typing import List

from pydantic import BaseModel, Field


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
    """Response model for entity list queries."""

    entities: list[dict[str, Any]] = Field(
        description="List of entities with their metadata"
    )
    count: int = Field(description="Total number of entities returned")


class LabelValue(BaseModel):
    """Individual label entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class DescriptionValue(BaseModel):
    """Individual description entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class AliasValue(BaseModel):
    """Individual alias entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class EntityLabels(BaseModel):
    """Collection of labels keyed by language code."""

    data: dict[str, LabelValue] = Field(default_factory=dict)


class EntityDescriptions(BaseModel):
    """Collection of descriptions keyed by language code."""

    data: dict[str, DescriptionValue] = Field(default_factory=dict)


class EntityAliases(BaseModel):
    """Collection of aliases keyed by language code."""

    data: dict[str, list[AliasValue]] = Field(default_factory=dict)


class EntityStatements(BaseModel):
    """List of entity statements."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class EntitySitelinks(BaseModel):
    """Collection of sitelinks."""

    data: dict[str, Any] = Field(default_factory=dict)


class EntityMetadata(BaseModel):
    """Model for entity metadata."""

    id: str
    type: str = Field(default="item")
    labels: EntityLabels = Field(default_factory=lambda: EntityLabels())
    descriptions: EntityDescriptions = Field(
        default_factory=lambda: EntityDescriptions()
    )
    aliases: EntityAliases = Field(default_factory=lambda: EntityAliases())
    statements: EntityStatements = Field(default_factory=lambda: EntityStatements())
    sitelinks: EntitySitelinks = Field(default_factory=lambda: EntitySitelinks())


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


class EntityJsonImportResponse(BaseModel):
    """Response model for JSONL entity import operations."""

    processed_count: int = Field(description="Number of lines processed")
    imported_count: int = Field(description="Number of entities successfully imported")
    failed_count: int = Field(description="Number of entities that failed to import")
    error_log_path: str = Field(
        description="Path to error log file for malformed lines"
    )
