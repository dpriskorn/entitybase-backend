"""Response models for endorsement operations."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from models.endorsements import Endorsement


class EndorsementResponse(BaseModel):
    """Response for endorsement operations."""

    model_config = ConfigDict(by_alias=True)

    endorsement_id: int = Field(alias="id", description="Unique identifier for the endorsement. Example: 12345.")
    user_id: int = Field(description="ID of the user who created the endorsement. Example: 67890.")
    statement_hash: int = Field(alias="hash", description="Hash of the endorsed statement. Example: 987654321.")
    created_at: str = Field(description="Timestamp when the endorsement was created (ISO format). Example: '2023-01-01T12:00:00Z'.")
    removed_at: Optional[str] = Field(default=None, description="Timestamp when the endorsement was removed (ISO format), null if active. Example: '2023-12-31T23:59:59Z'.")


class EndorsementListResponse(BaseModel):
    """Response for endorsement list queries."""

    statement_hash: int = Field(default=0)
    user_id: int = Field(default=0)
    endorsements: List[Endorsement]
    total_count: int
    has_more: bool
    stats: "StatementEndorsementStats"


class EndorsementStatsResponse(BaseModel):
    """Response for endorsement statistics."""

    user_id: int
    total_endorsements_given: int
    total_endorsements_active: int


class StatementEndorsementStats(BaseModel):
    """Response for statement endorsement statistics."""

    total: int
    active: int
    withdrawn: int


class BatchEndorsementStatsResponse(BaseModel):
    """Response for batch statement endorsement statistics."""

    stats: List[StatementEndorsementStats]


class SingleEndorsementStatsResponse(BaseModel):
    """Response for single statement endorsement statistics."""

    total: int
    active: int
    withdrawn: int
