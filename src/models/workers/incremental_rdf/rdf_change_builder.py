"""RDF Change Event builder for incremental RDF diff output."""

import uuid
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field


class RDFDataField(BaseModel):
    """RDF data field with mime type and data."""

    data: str = Field(..., description="The RDF data encoded using mime_type")
    mime_type: str = Field(default="text/turtle", description="Mime type of the RDF data")


class RDFChangeEvent(BaseModel):
    """RDF change event following entity_diff/2.0.0 schema.

    This schema represents a change in the RDF structure of a Wikibase entity.
    The event may happen for different reasons:
    - import: when an entity is created or restored
    - diff: when an entity is edited (new revision)
    - delete: when an entity is deleted
    - reconcile: to indicate prior data may no longer be trusted
    """

    model_config = {"extra": "forbid"}

    # Schema identifier
    schema: str = Field(
        default="/mediawiki/wikibase/entity/rdf_change/2.0.0",
        alias="$schema",
    )

    # Timestamp
    dt: str = Field(..., description="ISO-8601 formatted timestamp of when the event occurred")

    # Entity identification
    entity_id: str = Field(..., description="Wikibase entity ID being modified")

    # Meta information
    meta: dict = Field(
        ...,
        description="Meta object containing stream, domain, request_id, etc.",
    )

    # Operation type
    operation: str = Field(
        ...,
        description="Type of update: diff, import, delete, or reconcile",
    )

    # Revision
    rev_id: int = Field(..., description="The (database) revision ID related to this change")

    # RDF data fields
    rdf_added_data: Optional[RDFDataField] = Field(
        default=None,
        description="The triples that must be added",
    )
    rdf_deleted_data: Optional[RDFDataField] = Field(
        default=None,
        description="The triples that must be deleted",
    )
    rdf_linked_shared_data: Optional[RDFDataField] = Field(
        default=None,
        description="The triples that might be shared by other entities",
    )
    rdf_unlinked_shared_data: Optional[RDFDataField] = Field(
        default=None,
        description="Triples no longer linked from this entity",
    )

    # Sequence for chunking
    sequence: int = Field(default=0, description="Sequence number for multi-part events")
    sequence_length: int = Field(
        default=1, description="Number of messages to reconstruct the event"
    )


class RDFChangeEventBuilder:
    """Builder for RDF change events following entity_diff/2.0.0 schema."""

    @dataclass
    class EventConfig:
        """Configuration for building an RDF change event."""

        entity_id: str
        rev_id: int
        operation: str
        rdf_added_data: str
        rdf_deleted_data: str
        timestamp: str
        domain: str = "wikibase.org"
        request_id: Optional[str] = None

    @staticmethod
    def build(config: "RDFChangeEventBuilder.EventConfig") -> RDFChangeEvent:
        """Build an RDF change event.

        Args:
            config: Event configuration

        Returns:
            RDFChangeEvent following entity_diff/2.0.0 schema
        """
        request_id = config.request_id or str(uuid.uuid4())

        meta = {
            "domain": config.domain,
            "stream": "incremental_rdf_diff",
            "request_id": request_id,
        }

        added_field = None
        deleted_field = None

        if config.operation == "diff":
            if config.rdf_added_data:
                added_field = RDFDataField(data=config.rdf_added_data)
            if config.rdf_deleted_data:
                deleted_field = RDFDataField(data=config.rdf_deleted_data)
        elif config.operation == "import":
            if config.rdf_added_data:
                added_field = RDFDataField(data=config.rdf_added_data)
        elif config.operation == "delete":
            pass  # No RDF data for delete

        return RDFChangeEvent(
            dt=config.timestamp,
            entity_id=config.entity_id,
            meta=meta,
            operation=config.operation,
            rev_id=config.rev_id,
            rdf_added_data=added_field,
            rdf_deleted_data=deleted_field,
            sequence=0,
            sequence_length=1,
        )
