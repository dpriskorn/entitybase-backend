"""Event models for stream publishing."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from models.data.infrastructure.stream.actions import EndorseAction
from models.data.infrastructure.stream.change_type import ChangeType


class EndorseChangeEvent(BaseModel):
    """Endorsement change event for publishing."""

    model_config = ConfigDict(populate_by_name=True)

    statement_hash: str = Field(
        alias="hash", description="Hash of the endorsed statement"
    )
    user_id: str = Field(
        alias="user", description="ID of the user performing the action"
    )
    action: EndorseAction = Field(alias="act", description="Action performed")
    timestamp: datetime = Field(alias="ts", description="Timestamp of the action")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"


class NewThankEvent(BaseModel):
    """New thank event for publishing."""

    model_config = ConfigDict(populate_by_name=True)

    from_user_id: str = Field(alias="from", description="ID of the user sending thanks")
    to_user_id: str = Field(alias="to", description="ID of the user receiving thanks")
    entity_id: str = Field(alias="id", description="Entity ID related to the thanks")
    revision_id: int = Field(
        alias="rev", description="Revision ID related to the thanks"
    )
    timestamp: datetime = Field(alias="ts", description="Timestamp of the thanks")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"


class EntityChangeEvent(BaseModel):
    """Entity change event for publishing to Redpanda."""

    model_config = ConfigDict(populate_by_name=True)

    entity_id: str = Field(alias="id", description="Entity ID (e.g., Q42)")
    revision_id: int = Field(alias="rev", description="Revision ID of the change")
    change_type: "ChangeType" = Field(alias="type", description="Type of change")
    from_revision_id: Optional[int] = Field(
        alias="from_rev",
        default=None,
        description="Previous revision ID (None for creations)",
    )
    changed_at: datetime = Field(alias="at", description="Timestamp of change")
    edit_summary: str = Field(alias="summary", default="", description="Edit summary")

    @field_serializer("changed_at")
    def serialize_changed_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"
