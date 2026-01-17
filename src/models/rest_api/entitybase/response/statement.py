"""Statement response models."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class StatementResponse(BaseModel):
    """Response model for statement data."""

    model_config = ConfigDict(by_alias=True, populate_by_name=True)

    schema_version: str = Field(
        alias="schema", description="Schema version for the statement. Example: '1.0'."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the statement content. Example: 123456789."
    )
    statement: Dict[str, Any] = Field(
        description="Full statement JSON object. Example: {'id': 'P31', 'value': 'Q5'}."
    )
    created_at: str = Field(
        description="Timestamp when statement was created. Example: '2023-01-01T12:00:00Z'."
    )


class StatementBatchResponse(BaseModel):
    """Response model for batch statement queries."""

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


class MostUsedStatementsResponse(BaseModel):
    statements: list[int] = Field(
        default_factory=list,
        description="List of statement hashes sorted by ref_count DESC",
    )


class StatementHashResult(BaseModel):
    model_config = ConfigDict()

    statements: list[int] = Field(
        default_factory=list,
        description="List of statement hashes (rapidhash of each statement). Example: [123456789, 987654321].",
    )
    properties: list[str] = Field(
        default_factory=list,
        description="Sorted list of unique property IDs. Example: ['P31', 'P279'].",
    )
    property_counts: dict[str, int] = Field(
        alias="counts",
        default_factory=dict,
        description="Dict mapping property ID to count of statements. Example: {'P31': 5}.",
    )
    full_statements: list[Dict[str, Any]] = Field(
        alias="statements",
        default_factory=list,
        description="List of full statement dicts (parallel with hashes). Example: [{'id': 'P31', 'value': 'Q5'}].",
    )


class PropertyCounts(BaseModel):
    """Model for property statement counts."""

    counts: dict[str, int] = Field(
        description="Dictionary mapping property ID to statement count"
    )


class StatementsResponse(BaseModel):
    """Response model for statements."""

    statements: dict[str, Any] = Field(..., description="Statements data")
