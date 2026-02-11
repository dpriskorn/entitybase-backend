"""Miscellaneous response models."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


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


class RevisionMetadataResponse(BaseModel):
    """Metadata for entity revisions."""

    revision_id: int = Field(description="Revision ID")
    created_at: str = Field(description="Creation timestamp")
    user_id: int = Field(description="User ID")
    edit_summary: str = Field(description="Edit summary")


class LabelResponse(BaseModel):
    """Response model for entity labels."""

    value: str = Field(..., description="The label text for the specified language")


class DescriptionResponse(BaseModel):
    """Response model for entity descriptions."""

    value: str = Field(
        ..., description="The description text for the specified language"
    )


class AliasesResponse(BaseModel):
    """Response model for entity aliases."""

    aliases: list[str] = Field(
        ..., description="List of alias texts for the specified language"
    )


# class Aliases(BaseModel):
#     """Model for extracted aliases dictionary."""
#
#     aliases: dict[str, list[str]] = Field(..., description="Aliases per language")


class LabelsResponse(BaseModel):
    """Response model for all entity labels."""

    labels: dict[str, str] = Field(..., description="Labels per language")


class DescriptionsResponse(BaseModel):
    """Response model for all entity descriptions."""

    descriptions: dict[str, str] = Field(..., description="Descriptions per language")


class SitelinksResponse(BaseModel):
    """Response model for all entity sitelinks."""

    sitelinks: dict[str, str] = Field(..., description="Sitelinks per site")


class PropertiesResponse(BaseModel):
    """Response model for entity properties."""

    properties: dict[str, Any] = Field(..., description="Entity properties")


class EntitiesResponse(BaseModel):
    """Response model for entities search."""

    entities: dict[str, Any] = Field(..., description="Entities data")


class WatchCounts(BaseModel):
    """Model for user watch counts."""

    entity_count: int = Field(..., description="Number of entities watched")
    property_count: int = Field(..., description="Number of properties watched")


class RangeStatus(BaseModel):
    """Model for ID range status."""

    current_start: int = Field(..., description="Current range start ID")
    current_end: int = Field(..., description="Current range end ID")
    next_id: int = Field(..., description="Next available ID")
    ids_used: int = Field(..., description="Number of IDs used")
    utilization: float = Field(..., description="Utilization percentage")


class RangeStatuses(BaseModel):
    """Model for all ID range statuses."""

    ranges: dict[str, RangeStatus] = Field(
        ..., description="Range statuses by entity type"
    )


class TermsResponse(BaseModel):
    """Model for batch terms result."""

    terms: dict[int, tuple[str, str]] = Field(..., description="Terms by hash")


class MetadataContent(BaseModel):
    """Model for metadata content."""

    ref_count: int = Field(..., description="Reference count")


class MetadataData(BaseModel):
    """Model for metadata data content."""

    model_config = {"extra": "allow"}

    data: str | dict[str, Any] = Field(
        ..., description="Metadata content as text or structured data"
    )


class TopEntityByBacklinks(BaseModel):
    """Model for entity backlink ranking."""

    entity_id: str = Field(..., description="Entity ID")
    backlink_count: int = Field(..., description="Number of backlinks to this entity")


class TermsPerLanguage(BaseModel):
    """Model for terms count per language."""

    model_config = ConfigDict(extra="allow")

    terms: dict[str, int] = Field(description="Language to count mapping.")


class TermsByType(BaseModel):
    """Model for terms count by type."""

    model_config = ConfigDict(extra="allow")

    counts: dict[str, int] = Field(description="Type to count mapping.")


class GeneralStatsResponse(BaseModel):
    """API response for general wiki statistics."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(description="Date of statistics computation.")
    total_statements: int = Field(description="Total number of statements.")
    total_qualifiers: int = Field(description="Total number of qualifiers.")
    total_references: int = Field(description="Total number of references.")
    total_items: int = Field(description="Total number of items.")
    total_lexemes: int = Field(description="Total number of lexemes.")
    total_properties: int = Field(description="Total number of properties.")
    total_sitelinks: int = Field(description="Total number of sitelinks.")
    total_terms: int = Field(
        description="Total number of terms (labels + descriptions + aliases)."
    )
    terms_per_language: TermsPerLanguage = Field(
        description="Terms count per language."
    )
    terms_by_type: TermsByType = Field(
        description="Terms count by type (labels, descriptions, aliases)."
    )


# class RawRevisionResponse(BaseModel):
#     """Response model for raw revision data."""
#
#     data: dict[str, Any] = Field(..., description="Raw revision data from storage")


class TurtleResponse(BaseModel):
    """Response model for Turtle format entity data."""

    turtle: str = Field(..., description="Entity data in Turtle format")


class EntityJsonResponse(BaseModel):
    """Response model for JSON format entity data."""

    data: Dict[str, Any] = Field(..., description="Entity data in JSON format")
