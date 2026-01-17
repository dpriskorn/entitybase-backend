"""Event models for stream publishing."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from models.infrastructure.stream.change_type import ChangeType


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
    change_type: ChangeType = Field(alias="type", description="Type of change")
    from_revision_id: Optional[int] = Field(
        alias="from_rev",
        default=None,
        description="Previous revision ID (None for creations)",
    )
    changed_at: datetime = Field(alias="at", description="Timestamp of change")
    edit_summary: str = Field(alias="sum", default="", description="Edit summary")

    @field_serializer("changed_at")
    def serialize_changed_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"


class RDFChangeEvent(BaseModel):
    """RDF change event following MediaWiki recentchange schema."""

    model_config = ConfigDict(populate_by_name=True)

    # Required fields from schema
    schema_uri: str = Field(
        default="/wikibase/entity_diff/1.0.0",
        alias="$schema",
        description="Schema URI for the event",
    )
    type: str = Field(default="change", description="Event type")
    namespace: int = Field(description="Namespace of the changed entity")
    title: str = Field(description="Title of the changed entity")
    comment: str = Field(description="Edit comment")
    timestamp: int = Field(description="Unix timestamp of the change")
    user: str = Field(description="Username of the editor")
    bot: bool = Field(description="Whether the edit was made by a bot")
    log_id: int = Field(default=0, description="Log ID if applicable")
    log_type: str = Field(default="", description="Log type")
    log_action: str = Field(default="", description="Log action")
    server_url: str = Field(description="Server URL")
    server_name: str = Field(description="Server name")
    server_script_path: str = Field(description="Script path")
    wiki: str = Field(description="Wiki identifier")

    # Optional fields
    id: int = Field(default=0, description="Event ID")
    minor: bool = Field(default=False, description="Minor edit flag")
    patrolled: bool = Field(default=False, description="Patrolled flag")
    length: dict = Field(default_factory=dict, description="Length changes")
    revision: dict = Field(default_factory=dict, description="Revision details")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: int) -> str:
        """Serialize timestamp to ISO format."""
        return datetime.fromtimestamp(value).isoformat() + "Z"
