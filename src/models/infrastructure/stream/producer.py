\"\"\"Kafka streaming infrastructure for publishing change events.\"\"\"

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel, ConfigDict, Field, field_serializer

logger = logging.getLogger(__name__)


class EndorseAction(str, Enum):
    \"\"\"Actions for endorsement changes.\"\"\"

    ENDORSE = \"endorse\"
    WITHDRAW = \"withdraw\"


class EndorseChangeEvent(BaseModel):
    \"\"\"Endorsement change event for publishing.\"\"\"

    model_config = ConfigDict()

    statement_hash: str = Field(
        alias=\"hash\", description=\"Hash of the endorsed statement\"
    )
    user_id: str = Field(
        alias=\"user\", description=\"ID of the user performing the action\"
    )
    action: EndorseAction = Field(alias=\"act\", description=\"Action performed\")
    timestamp: datetime = Field(alias=\"ts\", description=\"Timestamp of the action\")

    @field_serializer(\"timestamp\")
    def serialize_timestamp(self, value: datetime) -> str:
        \"\"\"Serialize datetime to ISO format with Z suffix.\"\"\"
        return value.isoformat() + \"Z\"


class NewThankEvent(BaseModel):
    \"\"\"New thank event for publishing.\"\"\"

    model_config = ConfigDict()

    from_user_id: str = Field(alias=\"from\", description=\"ID of the user sending thanks\")
    to_user_id: str = Field(alias=\"to\", description=\"ID of the user receiving thanks\")
    entity_id: str = Field(alias=\"id\", description=\"Entity ID related to the thanks\")
    revision_id: int = Field(
        alias=\"rev\", description=\"Revision ID related to the thanks\"
    )
    timestamp: datetime = Field(alias=\"ts\", description=\"Timestamp of the thanks\")

    @field_serializer(\"timestamp\")
    def serialize_timestamp(self, value: datetime) -> str:
        \"\"\"Serialize datetime to ISO format with Z suffix.\"\"\"
        return value.isoformat() + \"Z\"


class RDFChangeEvent(BaseModel):
    \"\"\"RDF change event following MediaWiki recentchange schema.\"\"\"

    # Required fields from schema
    schema_uri: str = Field(
        default=\"/wikibase/entity_diff/1.0.0\",
        alias=\"$schema\",
        description=\"Schema URI for this event\",
    )
    meta: dict = Field(..., description=\"Event metadata\")

    # Wikibase-specific fields
    entity_id: str = Field(..., description=\"Entity ID (e.g., Q42)\")
    revision_id: int = Field(..., description=\"New revision ID\")
    from_revision_id: int = Field(
        default=0, description=\"Previous revision ID (0 for creation)\"
    )
    # RDF diff data
    added_triples: list[tuple[str, str, str]] = Field(
        default_factory=list, description=\"RDF triples added in this revision\"
    )
    removed_triples: list[tuple[str, str, str]] = Field(
        default_factory=list, description=\"RDF triples removed in this revision\"
    )

    # Canonicalization metadata
    canonicalization_method: str = Field(
        default=\"urdna2015\", description=\"RDF canonicalization method used\"
    )
    triple_count_diff: int = Field(..., description=\"Net change in triple count\")

    # MediaWiki recentchange schema fields
    type: str = Field(default=\"edit\", description=\"Type of change\")
    title: str = Field(..., description=\"Entity title\")
    user: str = Field(..., description=\"Editor username\")
    timestamp: int = Field(..., description=\"Unix timestamp\")
    comment: str = Field(default=\"\", description=\"Edit summary\")
    bot: bool = Field(default=False, description=\"Whether editor is a bot\")
    minor: bool = Field(default=False, description=\"Whether this is a minor edit\")
    patrolled: bool | None = Field(None, description=\"Patrol status\")

    # Revision info following schema
    revision: dict = Field(
        default_factory=lambda: {\"new\": None, \"old\": None},
        description=\"Old and new revision IDs\",
    )

    # Length info
    length: dict = Field(
        default_factory=lambda: {\"new\": None, \"old\": None},
        description=\"Length of old and new revisions\",
    )

    # Additional fields
    namespace: int = Field(default=0, description=\"Namespace ID\")
    server_name: str = Field(..., description=\"Server name\")
    server_url: str = Field(..., description=\"Server URL\")
    wiki: str = Field(..., description=\"Wiki identifier\")

    @field_serializer(\"added_triples\", \"removed_triples\")
    def serialize_triples(self, value: list[tuple[str, str, str]]) -> list[list[str]]:
        \"\"\"Serialize triple tuples to lists for JSON.\"\"\"
        return [list(triple) for triple in value]

    model_config = ConfigDict()


class StreamProducerClient:
    """Kafka producer client for publishing events."""

    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Start the Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: v.model_dump_json(by_alias=True).encode("utf-8"),
        )
        await self.producer.start()
        logger.info(f"Started Kafka producer for topic {self.topic}")

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            self.producer = None
            logger.info("Stopped Kafka producer")

    async def publish_change(self, event: Any) -> None:
        """Publish an event to Kafka."""
        if not self.producer:
            logger.warning("Kafka producer not started, skipping event publish")
            return

        try:
            key = getattr(event, "entity_id", getattr(event, "hash", None))
            if key is None:
                logger.error(f"Event {event} has no key field")
                return

            await self.producer.send_and_wait(
                topic=self.topic,
                key=str(key),
                value=event,
            )
            logger.debug(f"Published event: {event}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")