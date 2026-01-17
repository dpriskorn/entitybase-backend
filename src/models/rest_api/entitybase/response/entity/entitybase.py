from typing import Dict, Any

from pydantic import BaseModel, Field

from models.rest_api.entitybase.response.entity.wikibase import SitelinkValue, LabelValue, DescriptionValue, AliasValue
from models.validation.utils import raise_validation_error



class EntityLabelsResponse(BaseModel):
    """Collection of labels keyed by language code."""

    data: dict[str, LabelValue] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> LabelValue:
        return self.data[key]

    def get(self, language_code: str) -> LabelValue:
        """Get label for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Label not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityDescriptionsResponse(BaseModel):
    """Collection of descriptions keyed by language code."""

    data: dict[str, DescriptionValue] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> DescriptionValue:
        return self.data[key]

    def get(self, language_code: str) -> DescriptionValue:
        """Get description for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Description not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityAliasesResponse(BaseModel):
    """Collection of aliases keyed by language code."""

    data: dict[str, list[AliasValue]] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> list[AliasValue]:
        return self.data[key]

    def get(self, language_code: str) -> list[AliasValue]:
        """Get aliases for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Aliases not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityStatementsResponse(BaseModel):
    """List of entity statements."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class EntitySitelinksResponse(BaseModel):
    """Collection of sitelinks."""

    data: dict[str, SitelinkValue] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> SitelinkValue:
        return self.data[key]

    def get(self, site: str) -> SitelinkValue:
        """Get sitelink for the specified site."""
        if not site:
            raise_validation_error("Site cannot be empty", status_code=400)
        if site not in self.data:
            raise_validation_error(
                f"Sitelink not found for site {site}", status_code=404
            )
        return self.data[site]


class EntityHistoryEntry(BaseModel):
    """Response model for a single entity history entry."""

    revision_id: int
    created_at: str | None
    user_id: int | None
    edit_summary: str | None


class EntityResponse(BaseModel):
    """Response model for entity data."""

    id: str
    revision_id: int
    entity_data: Dict[str, Any]
    is_semi_protected: bool = False
    is_locked: bool = False
    is_archived: bool = False
    is_dangling: bool = False
    is_mass_edit_protected: bool = False


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


class EntityMetadataResponse(BaseModel):
    """Model for entity metadata."""

    id: str
    type: str = Field(default="item")
    labels: EntityLabelsResponse = Field(default_factory=lambda: EntityLabelsResponse())
    descriptions: EntityDescriptionsResponse = Field(
        default_factory=lambda: EntityDescriptionsResponse()
    )
    aliases: EntityAliasesResponse = Field(
        default_factory=lambda: EntityAliasesResponse()
    )
    statements: EntityStatementsResponse = Field(
        default_factory=lambda: EntityStatementsResponse()
    )
    sitelinks: EntitySitelinksResponse = Field(
        default_factory=lambda: EntitySitelinksResponse()
    )


class EntityMetadataBatchResponse(BaseModel):
    """Response model for batch entity metadata fetching."""

    metadata: dict[str, EntityMetadataResponse | None] = Field(
        description="Dictionary mapping entity_id to metadata or None"
    )


class EntityRevisionResponse(BaseModel):
    """Model for entity revision response."""

    entity_id: str
    revision_id: int
    revision_data: dict[str, Any] = Field(description="Revision data")


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
