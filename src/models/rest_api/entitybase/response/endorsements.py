"""Response models for endorsement operations."""

from typing import List, Optional

from pydantic import BaseModel, Field

from models.endorsements import StatementEndorsement


class EndorsementResponse(BaseModel):
    """Response for endorsement operations."""

    endorsement_id: int
    user_id: int
    statement_hash: int
    created_at: str  # ISO format datetime string
    removed_at: Optional[str] = Field(default=None)


class EndorsementListResponse(BaseModel):
    """Response for endorsement list queries."""

    statement_hash: Optional[int] = Field(default=None)
    user_id: Optional[int] = Field(default=None)
    endorsements: List[StatementEndorsement]
    total_count: int
    has_more: bool
    stats: StatementEndorsementStats


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