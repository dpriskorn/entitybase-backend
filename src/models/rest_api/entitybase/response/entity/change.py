"""Response schemas for entity change data."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from models.infrastructure.stream.change_type import ChangeType


class EntityChange(BaseModel):
    """Schema for entity change events in API responses."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    entity_id: str = Field(..., description="The ID of the entity that changed")
    revision_id: int = Field(..., description="The new revision ID after the change")
    change_type: "ChangeType" = Field(..., description="The type of change")
    from_revision_id: int = Field(
        0, description="The previous revision ID (0 for creations)"
    )
    changed_at: datetime = Field(..., description="Timestamp of the change")
    edit_summary: str = Field("", description="Summary of the edit")
