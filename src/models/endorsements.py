"""Endorsement models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StatementEndorsement(BaseModel):
    """Endorsement record."""

    id: int
    user_id: int
    statement_hash: int
    created_at: datetime
    removed_at: Optional[datetime] = Field(default=None)


class Endorsement(BaseModel):
    """Endorsement record."""

    id: int
    user_id: int
    statement_hash: int
    created_at: datetime
    removed_at: Optional[datetime] = Field(default=None)


class EndorsementStats(BaseModel):
    """Endorsement statistics for a user."""

    user_id: int
    total_endorsements_given: int
    total_endorsements_active: int
