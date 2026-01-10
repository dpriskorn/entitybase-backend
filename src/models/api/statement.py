from typing import Any, Dict

from pydantic import BaseModel, Field


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


class PropertyCounts(BaseModel):
    """Model for property statement counts."""

    counts: dict[str, int] = Field(
        description="Dictionary mapping property ID to statement count"
    )
