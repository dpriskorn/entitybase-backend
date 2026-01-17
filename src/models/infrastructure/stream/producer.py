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

    async def publish_rdf_change(self, event: "RDFChangeEvent") -> None:
        """Publish RDF change event to Kafka."""
        if self.producer is None:
            logger.warning("Kafka producer not started, skipping RDF change event")
            return

        try:
            await self.producer.send_and_wait(
                topic=self.topic,
                key=event.entity_id,
                value=event,
            )
            logger.debug(
                f"Published RDF change event: entity={event.entity_id}, "
                f"revision={event.revision_id}, added={len(event.added_triples)}, "
                f"removed={len(event.removed_triples)}"
            )
        except Exception as e:
            logger.error(
                f"Failed to publish RDF change event for {event.entity_id}: {e}",
                exc_info=True,
            )


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


class RDFChangeType(str, Enum):
    """RDF change event types for streaming to Redpanda."""

    ENTITY_DIFF = "entity_diff"


class EntityChangeEvent(BaseModel):
    """Entity change event for publishing to Redpanda."""

    entity_id: str = Field(alias="id", description="Entity ID (e.g., Q42)")
    revision_id: int = Field(alias="rev", description="Revision ID of the change")
    change_type: ChangeType = Field(alias="type", description="Type of change")
    from_revision_id: int = Field(
        alias="from_rev", default=0, description="Previous revision ID (0 for creation)"
    )
    changed_at: datetime = Field(alias="at", description="Timestamp of change")
    editor: str = Field(alias="ed", default="", description="Editor who made the change")
    edit_summary: str = Field(alias="sum", default="", description="Edit summary")

    @field_serializer("changed_at")
    def serialize_changed_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"

    model_config = ConfigDict(by_alias=True)


class EndorseChangeEvent(BaseModel):
    """Endorsement change event for publishing."""

    statement_hash: str = Field(alias="hash", description="Hash of the endorsed statement")
    user_id: str = Field(alias="user", description="ID of the user performing the action")
    action: str = Field(alias="act", description="Action: 'endorse' or 'withdraw'")
    timestamp: datetime = Field(alias="ts", description="Timestamp of the action")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"

    model_config = ConfigDict(by_alias=True)


class NewThankEvent(BaseModel):
    """New thank event for publishing."""

    from_user_id: str = Field(alias="from", description="ID of the user sending thanks")
    to_user_id: str = Field(alias="to", description="ID of the user receiving thanks")
    entity_id: str = Field(alias="id", description="Entity ID related to the thanks")
    revision_id: int = Field(alias="rev", description="Revision ID related to the thanks")
    timestamp: datetime = Field(alias="ts", description="Timestamp of the thanks")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return value.isoformat() + "Z"

    model_config = ConfigDict(by_alias=True)


class RDFChangeEvent(BaseModel):
    """RDF change event following MediaWiki recentchange schema."""

    # Required fields from schema
    schema_uri: str = Field(
        default="/wikibase/entity_diff/1.0.0",
        alias="$schema",
        description="Schema URI for this event",
    )
    meta: dict = Field(..., description="Event metadata")

    # Wikibase-specific fields
    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    revision_id: int = Field(..., description="New revision ID")
    from_revision_id: int = Field(
        default=0, description="Previous revision ID (0 for creation)"
    )
    # RDF diff data
    added_triples: list[tuple[str, str, str]] = Field(
        default_factory=list, description="RDF triples added in this revision"
    )
    removed_triples: list[tuple[str, str, str]] = Field(
        default_factory=list, description="RDF triples removed in this revision"
    )

    # Canonicalization metadata
    canonicalization_method: str = Field(
        default="urdna2015", description="RDF canonicalization method used"
    )
    triple_count_diff: int = Field(..., description="Net change in triple count")

    # MediaWiki recentchange schema fields
    type: str = Field(default="edit", description="Type of change")
    title: str = Field(..., description="Entity title")
    user: str = Field(..., description="Editor username")
    timestamp: int = Field(..., description="Unix timestamp")
    comment: str = Field(default="", description="Edit summary")
    bot: bool = Field(default=False, description="Whether editor is a bot")
    minor: bool = Field(default=False, description="Whether this is a minor edit")
    patrolled: bool | None = Field(None, description="Patrol status")

    # Revision info following schema
    revision: dict = Field(
        default_factory=lambda: {"new": None, "old": None},
        description="Old and new revision IDs",
    )

    # Length info
    length: dict = Field(
        default_factory=lambda: {"new": None, "old": None},
        description="Length of old and new revisions",
    )

    # Additional fields
    namespace: int = Field(default=0, description="Namespace ID")
    server_name: str = Field(..., description="Server name")
    server_url: str = Field(..., description="Server URL")
    wiki: str = Field(..., description="Wiki identifier")

    @field_serializer("added_triples", "removed_triples")
    def serialize_triples(self, value: list[tuple[str, str, str]]) -> list[list[str]]:
        """Serialize triple tuples to lists for JSON."""
        return [list(triple) for triple in value]

    model_config = ConfigDict()
