"""Response models for endorsement operations."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EndorsementResponse(BaseModel):
    """Response for endorsement operations."""

    model_config = ConfigDict()

    endorsement_id: int = Field(
        alias="id", description="Unique identifier for the endorsement. Example: 12345."
    )
    user_id: int = Field(
        description="ID of the user who created the endorsement. Example: 67890."
    )
    statement_hash: int = Field(
        alias="hash", description="Hash of the endorsed statement. Example: 987654321."
    )
    created_at: str = Field(
        description="Timestamp when the endorsement was created (ISO format). Example: '2023-01-01T12:00:00Z'."
    )
    removed_at: str = Field(
        default="",
        description="Timestamp when the endorsement was removed (ISO format), empty string if active. Example: '2023-12-31T23:59:59Z'.",
    )


class EndorsementListResponse(BaseModel):
    """Response for endorsement list queries."""

    model_config = ConfigDict()

    statement_hash: int = Field(
        alias="hash",
        default=0,
        description="Hash of the statement for which endorsements are listed. Example: 12345",
    )
    user_id: int = Field(
        default=0,
        description="ID of the user whose endorsements are listed. Example: 67890",
    )
    endorsements: List[EndorsementResponse] = Field(
        alias="list",
        description="List of endorsements. Example: [{'id': 1, 'user_id': 123}]",
    )
    total_count: int = Field(
        alias="count", description="Total number of endorsements. Example: 50"
    )
    has_more: bool = Field(
        alias="more",
        description="Whether there are more endorsements to fetch. Example: true",
    )
    stats: Optional["StatementEndorsementStats"] = Field(
        default=None, description="Statistics for the statement's endorsements"
    )


class EndorsementStatsResponse(BaseModel):
    """Response for endorsement statistics."""

    model_config = ConfigDict()

    user_id: int = Field(
        description="ID of the user for whom statistics are provided. Example: 12345"
    )
    total_endorsements_given: int = Field(
        alias="given",
        description="Total number of endorsements given by the user. Example: 10",
    )
    total_endorsements_active: int = Field(
        alias="active",
        description="Number of active endorsements given by the user. Example: 8",
    )


class StatementEndorsementStats(BaseModel):
    """Response for statement endorsement statistics."""

    total: int = Field(
        description="Total number of endorsements for the statement. Example: 15"
    )
    active: int = Field(
        description="Number of active endorsements for the statement. Example: 12"
    )
    withdrawn: int = Field(
        description="Number of withdrawn endorsements for the statement. Example: 3"
    )


class BatchEndorsementStatsResponse(BaseModel):
    """Response for batch statement endorsement statistics."""

    stats: List[StatementEndorsementStats] = Field(
        description="List of endorsement statistics for multiple statements"
    )


class SingleEndorsementStatsResponse(BaseModel):
    """Response for single statement endorsement statistics."""

    total: int = Field(
        description="Total number of endorsements for the statement. Example: 15"
    )
    active: int = Field(
        description="Number of active endorsements for the statement. Example: 12"
    )
    withdrawn: int = Field(
        description="Number of withdrawn endorsements for the statement. Example: 3"
    )


class StatementEndorsementResponse(BaseModel):
    """Endorsement record."""

    id: int
    user_id: int
    statement_hash: int
    created_at: datetime
    removed_at: Optional[datetime] = Field(default=None)
