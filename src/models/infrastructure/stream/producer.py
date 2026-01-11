"""Kafka streaming infrastructure for publishing change events."""

import json
import logging
from datetime import datetime
from enum import Enum

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel, ConfigDict, Field, field_serializer

logger = logging.getLogger(__name__)


class StreamProducerClient(BaseModel):
    """Async Kafka producer client for publishing change events."""

    bootstrap_servers: str
    topic: str
    producer: AIOKafkaProducer | None = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v.model_dump()).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self.producer.start()
            logger.info(
                f"Kafka producer started: servers={self.bootstrap_servers}, topic={self.topic}"
            )

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None
            logger.info("Kafka producer stopped")

    async def publish_change(self, event: "EntityChangeEvent") -> None:
        """Publish entity change event to Kafka."""
        if self.producer is None:
            logger.warning("Kafka producer not started, skipping change event")
            return

        try:
            await self.producer.send_and_wait(
                topic=self.topic,
                key=event.entity_id,
                value=event,
            )
            logger.debug(
                f"Published change event: entity={event.entity_id}, "
                f"revision={event.revision_id}, type={event.change_type}"
            )
        except Exception as e:
            logger.error(
                f"Failed to publish change event for {event.entity_id}: {e}",
                exc_info=True,
            )

    async def publish_change_sync(self, event: "EntityChangeEvent") -> None:
        """Synchronous publish with delivery confirmation."""
        await self.publish_change(event)


class ChangeType(str, Enum):
    """Change event types for streaming to Redpanda."""

    CREATION = "creation"
    EDIT = "edit"
    REDIRECT = "redirect"
    UNREDIRECT = "unredirect"
    ARCHIVAL = "archival"
    UNARCHIVAL = "unarchival"
    LOCK = "lock"
    UNLOCK = "unlock"
    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"


class EntityChangeEvent(BaseModel):
    """Entity change event for publishing to Redpanda."""

    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    revision_id: int = Field(..., description="Revision ID of the change")
    change_type: ChangeType = Field(..., description="Type of change")
    from_revision_id: int | None = Field(
        None, description="Previous revision ID (null for creation)"
    )
    changed_at: datetime = Field(..., description="Timestamp of change")
    editor: str | None = Field(None, description="Editor who made the change")
    edit_summary: str | None = Field(None, description="Edit summary")

    @field_serializer("changed_at")
    def serialize_changed_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"

    model_config = ConfigDict()
