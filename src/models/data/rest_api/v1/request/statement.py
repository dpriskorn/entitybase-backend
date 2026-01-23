"""Statement request models."""

from pydantic import BaseModel, Field


class StatementBatchRequest(BaseModel):
    hashes: list[int] = Field(..., description="List of statement hashes to fetch")


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
