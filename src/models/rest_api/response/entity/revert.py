"""Response models for entity revert operations."""

from pydantic import BaseModel


class EntityRevertResponse(BaseModel):
    """Response for entity revert operation."""

    entity_id: str
    new_revision_id: int
    reverted_from_revision_id: int
    reverted_at: str
