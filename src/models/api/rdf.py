from pydantic import BaseModel, Field


class WikibasePredicates(BaseModel):
    """Model for Wikibase predicate URIs for a property."""

    direct: str = Field(description="Direct property predicate")
    statement: str = Field(description="Statement property predicate")
    statement_value: str = Field(description="Statement value property predicate")
    qualifier: str = Field(description="Qualifier property predicate")
    reference: str = Field(description="Reference property predicate")
    statement_value_node: str = Field(description="Statement value node predicate")


class DeduplicationStats(BaseModel):
    """Model for deduplication cache statistics."""

    hits: int = Field(description="Number of cache hits")
    misses: int = Field(description="Number of cache misses")
    size: int = Field(description="Current cache size")
    collision_rate: float = Field(description="Collision rate percentage")


class RedirectBatchResponse(BaseModel):
    """Response model for batch entity redirects fetching."""

    redirects: dict[str, list[str]] = Field(
        description="Dictionary mapping entity_id to list of redirect titles"
    )


class FullRevisionData(BaseModel):
    """Model for full revision data from database."""

    revision_id: int = Field(description="Revision ID")
    statements: list[int] = Field(description="List of statement hashes")
    properties: list[str] = Field(description="List of unique properties")
    property_counts: dict[str, int] = Field(description="Property counts")
    labels: dict[str, dict[str, str]] = Field(
        default_factory=dict, description="Entity labels"
    )
    descriptions: dict[str, dict[str, str]] = Field(
        default_factory=dict, description="Entity descriptions"
    )
    aliases: dict[str, list[str]] = Field(
        default_factory=dict, description="Entity aliases"
    )


class MetadataLoadResponse(BaseModel):
    """Response model for metadata loading operations."""

    results: dict[str, bool] = Field(
        description="Dictionary mapping entity_id to success status"
    )
