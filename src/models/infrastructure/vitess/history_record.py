"""Record of entity revision history."""

from pydantic import BaseModel


class HistoryRecord(BaseModel):
    """Record of entity revision history."""

    revision_id: int
    created_at: str
    is_mass_edit: bool = False