"""Statistics response models."""

from pydantic import BaseModel, ConfigDict, Field

from models.data.rest_api.v1.entitybase.response.terms import (
    TermsByType,
    TermsPerLanguage,
)


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


class DeduplicationStatsByType(BaseModel):
    """Deduplication stats for a single data type."""

    unique_hashes: int = Field(description="Number of unique hashes stored")
    total_ref_count: int = Field(description="Total reference count (what would be stored without deduplication)")
    deduplication_factor: float = Field(description="Deduplication factor as a percentage (0-100)")
    space_saved: int = Field(description="Number of duplicates eliminated")


class DeduplicationStatsResponse(BaseModel):
    """API response for deduplication statistics."""

    statements: DeduplicationStatsByType = Field(description="Statement deduplication stats")
    qualifiers: DeduplicationStatsByType = Field(description="Qualifier deduplication stats")
    references: DeduplicationStatsByType = Field(description="Reference deduplication stats")
    snaks: DeduplicationStatsByType = Field(description="Snak deduplication stats")
    sitelinks: DeduplicationStatsByType = Field(description="Sitelink deduplication stats")
    terms: DeduplicationStatsByType = Field(description="Term deduplication stats")


class DeduplicationDatabaseStatsResponse(BaseModel):
    """API response for database deduplication statistics."""

    statements: DeduplicationStatsByType = Field(
        description="Statement deduplication stats"
    )
    qualifiers: DeduplicationStatsByType = Field(
        description="Qualifier deduplication stats"
    )
    references: DeduplicationStatsByType = Field(
        description="Reference deduplication stats"
    )
    snaks: DeduplicationStatsByType = Field(description="Snak deduplication stats")
    sitelinks: DeduplicationStatsByType = Field(
        description="Sitelink deduplication stats"
    )
    terms: DeduplicationStatsByType = Field(description="Term deduplication stats")


class GeneralStatsData(BaseModel):
    """Container for computed general wiki statistics."""

    model_config = ConfigDict(populate_by_name=True)

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
