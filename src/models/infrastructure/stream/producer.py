"""Kafka streaming infrastructure for publishing change events."""

import json
import logging
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class EndorseAction(str, Enum):
    """Actions for endorsement changes."""
    ENDORSE = "endorse"
    WITHDRAW = "withdraw"


class EndorseChangeEvent(BaseModel):
    """Endorsement change event for publishing."""

    statement_hash: str = Field(alias="hash", description="Hash of the endorsed statement")
    user_id: str = Field(alias="user", description="ID of the user performing the action")
    action: EndorseAction = Field(alias="act", description="Action performed")
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
