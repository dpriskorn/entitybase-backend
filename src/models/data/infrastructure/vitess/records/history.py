"""Record of entity revision history."""

from pydantic import BaseModel, Field


class HistoryRecord(BaseModel):
    """Record of entity revision history."""

    revision_id: int = Field(..., description="Revision identifier")
    created_at: str = Field(..., description="Timestamp when revision was created")
    is_mass_edit: bool = Field(default=False, description="Whether this revision was a mass edit")
