"""Response schemas for entity change data."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.infrastructure.stream.producer import ChangeType


class EntityChange(BaseModel):
    """Schema for entity change events in API responses."""

    model_config = ConfigDict(from_attributes=True)

    entity_id: str = Field(..., description="The ID of the entity that changed")
    revision_id: int = Field(..., description="The new revision ID after the change")
    change_type: ChangeType = Field(..., description="The type of change")
    from_revision_id: int = Field(0, description="The previous revision ID (0 for creations)")
    changed_at: datetime = Field(..., description="Timestamp of the change")
    edit_summary: str = Field("", description="Summary of the edit")
    bot: bool = Field(False, description="Whether the change was made by a bot")