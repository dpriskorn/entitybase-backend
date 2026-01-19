from typing import Dict, Any

from pydantic import BaseModel, ConfigDict, Field

from models.infrastructure.s3.revision.entity_state import EntityState
from models.rest_api.v1.entitybase.response.entity.wikibase import (
    SitelinkValue,
    LabelValue,
    DescriptionValue,
    AliasValue,
)
from models.rest_api.utils import raise_validation_error
from models.infrastructure.s3.revision.revision_data import RevisionData


class EntityLabelsResponse(BaseModel):
    """Collection of labels keyed by language code."""

    data: dict[str, LabelValue] = Field(
        default_factory=dict,
        description="Dictionary of labels keyed by language code. Example: {'en': {'language': 'en', 'value': 'Test'}}.",
    )

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

    data: dict[str, DescriptionValue] = Field(
        default_factory=dict,
        description="Dictionary of descriptions keyed by language code. Example: {'en': {'language': 'en', 'value': 'A test description'}}.",
    )

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

    data: dict[str, list[AliasValue]] = Field(
        default_factory=dict,
        description="Dictionary of aliases keyed by language code.",
    )

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

    data: list[dict[str, Any]] = Field(
        default_factory=list, description="List of entity statements."
    )


class EntitySitelinksResponse(BaseModel):
    """Collection of sitelinks."""

    data: dict[str, SitelinkValue] = Field(
        default_factory=dict, description="Dictionary of sitelinks keyed by site."
    )

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

    revision_id: int = Field(description="Revision ID. Example: 12345.")
    created_at: str = Field(
        default="",
        description="Creation timestamp (ISO format). Example: '2023-01-01T12:00:00Z'.",
    )
    user_id: int = Field(
        default=0, description="User ID who made the change. Example: 67890."
    )
    edit_summary: str = Field(
        default="",
        alias="summary",
        description="Edit summary text. Example: 'Added label'.",
    )


class EntityResponse(BaseModel):
    """Response model for entity data."""

    model_config = ConfigDict(populate_by_name=True)  # type: ignore[typeddict-unknown-key]

    id: str = Field(description="Entity ID. Example: 'Q42'.")
    revision_id: int = Field(
        alias="rev_id", description="Revision ID of the entity. Example: 12345."
    )
    entity_data: Dict[str, Any] = Field(
        alias="data",
        description="Full entity JSON data. Example: {'id': 'Q42', 'type': 'item'}.",
    )
    state: EntityState = Field(description="Entity state information.")


class EntityDeleteResponse(BaseModel):
    """Response model for entity deletion."""

    model_config = ConfigDict()

    id: str = Field(description="Entity ID. Example: 'Q42'.")
    revision_id: int = Field(
        alias="rev_id", description="Revision ID at deletion. Example: 12345."
    )
    is_deleted: bool = Field(description="Whether entity is deleted. Example: true.")
    deletion_type: str = Field(
        alias="del_type",
        description="Type of deletion performed. Example: 'soft_delete'.",
    )
    deletion_status: str = Field(
        alias="del_status",
        description="Status of deletion (soft_deleted/hard_deleted). Example: 'soft_deleted'.",
    )


class EntityRedirectResponse(BaseModel):
    """Response model for entity redirect creation."""

    redirect_from_id: str = Field(description="Entity ID being redirected from")
    redirect_to_id: str = Field(description="Entity ID being redirected to")
    created_at: str = Field(description="Creation timestamp of the redirect")
    revision_id: int = Field(description="Revision ID of the redirect")


class EntityListResponse(BaseModel):
    """Response model for entity list queries."""

    entities: list[dict[str, Any]] = Field(
        description="List of entities with their metadata"
    )
    count: int = Field(description="Total number of entities returned")


class EntityMetadataResponse(BaseModel):
    """Model for entity metadata."""

    id: str = Field(description="Entity ID")
    type: str = Field(default="item", description="Entity type")
    labels: EntityLabelsResponse = Field(
        default_factory=lambda: EntityLabelsResponse(), description="Entity labels"
    )
    descriptions: EntityDescriptionsResponse = Field(
        default_factory=lambda: EntityDescriptionsResponse(),
        description="Entity descriptions",
    )
    aliases: EntityAliasesResponse = Field(
        default_factory=lambda: EntityAliasesResponse(), description="Entity aliases"
    )
    statements: EntityStatementsResponse = Field(
        default_factory=lambda: EntityStatementsResponse(),
        description="Entity statements",
    )
    sitelinks: EntitySitelinksResponse = Field(
        default_factory=lambda: EntitySitelinksResponse(),
        description="Entity sitelinks",
    )


class EntityMetadataBatchResponse(BaseModel):
    """Response model for batch entity metadata fetching."""

    metadata: dict[str, EntityMetadataResponse | None] = Field(
        description="Dictionary mapping entity_id to metadata or None"
    )


class EntityRevisionResponse(BaseModel):
    """Model for entity revision response."""

    entity_id: str = Field(description="Entity ID")
    revision_id: int = Field(description="Revision ID")
    revision_data: RevisionData = Field(description="Revision data")


class ProtectionResponse(BaseModel):
    """Model for entity protection information."""

    model_config = ConfigDict(populate_by_name=True)

    is_semi_protected: bool = Field(
        alias="semi_prot",
        description="Whether entity is semi-protected. Example: true.",
    )
    is_locked: bool = Field(
        alias="locked", description="Whether entity is locked. Example: false."
    )
    is_archived: bool = Field(
        alias="archived", description="Whether entity is archived. Example: false."
    )
    is_dangling: bool = Field(
        alias="dangling", description="Whether entity is dangling. Example: false."
    )
    is_mass_edit_protected: bool = Field(
        alias="mass_edit",
        description="Whether entity is mass edit protected. Example: true.",
    )


class EntityJsonImportResponse(BaseModel):
    """Response model for JSONL entity import operations."""

    processed_count: int = Field(description="Number of lines processed")
    imported_count: int = Field(description="Number of entities successfully imported")
    failed_count: int = Field(description="Number of entities that failed to import")
    error_log_path: str = Field(
        description="Path to error log file for malformed lines"
    )
