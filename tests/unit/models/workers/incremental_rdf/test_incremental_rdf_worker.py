"""Unit tests for incremental_rdf_worker and rdf_change_builder."""

import pytest
from datetime import datetime, timezone

from models.workers.incremental_rdf.rdf_change_builder import (
    RDFChangeEvent,
    RDFChangeEventBuilder,
    RDFDataField,
)


class TestRDFDataField:
    """Test RDFDataField model."""

    def test_rdf_data_field_creation(self):
        """Test creating an RDFDataField."""
        field = RDFDataField(data="<test> a <test> .")
        assert field.data == "<test> a <test> ."
        assert field.mime_type == "text/turtle"

    def test_rdf_data_field_custom_mime_type(self):
        """Test creating an RDFDataField with custom mime type."""
        field = RDFDataField(data="<test>", mime_type="application/ld+json")
        assert field.data == "<test>"
        assert field.mime_type == "application/ld+json"


class TestRDFChangeEvent:
    """Test RDFChangeEvent model."""

    def test_rdf_change_event_diff_operation(self):
        """Test creating an RDFChangeEvent for diff operation."""
        event = RDFChangeEvent(
            dt="2024-01-01T00:00:00Z",
            entity_id="Q42",
            meta={"domain": "wikidata.org", "stream": "test"},
            operation="diff",
            rev_id=123,
            rdf_added_data=RDFDataField(data="<added>"),
            rdf_deleted_data=RDFDataField(data="<removed>"),
            sequence=0,
            sequence_length=1,
        )
        assert event.entity_id == "Q42"
        assert event.operation == "diff"
        assert event.rev_id == 123
        assert event.rdf_added_data is not None
        assert event.rdf_deleted_data is not None

    def test_rdf_change_event_import_operation(self):
        """Test creating an RDFChangeEvent for import operation."""
        event = RDFChangeEvent(
            dt="2024-01-01T00:00:00Z",
            entity_id="Q42",
            meta={"domain": "wikidata.org", "stream": "test"},
            operation="import",
            rev_id=123,
            rdf_added_data=RDFDataField(data="<full data>"),
            sequence=0,
            sequence_length=1,
        )
        assert event.operation == "import"
        assert event.rdf_added_data is not None
        assert event.rdf_deleted_data is None

    def test_rdf_change_event_delete_operation(self):
        """Test creating an RDFChangeEvent for delete operation."""
        event = RDFChangeEvent(
            dt="2024-01-01T00:00:00Z",
            entity_id="Q42",
            meta={"domain": "wikidata.org", "stream": "test"},
            operation="delete",
            rev_id=123,
            sequence=0,
            sequence_length=1,
        )
        assert event.operation == "delete"
        assert event.rdf_added_data is None
        assert event.rdf_deleted_data is None


class TestRDFChangeEventBuilder:
    """Test RDFChangeEventBuilder."""

    def test_build_diff_event(self):
        """Test building a diff event."""
        config = RDFChangeEventBuilder.EventConfig(
            entity_id="Q42",
            rev_id=123,
            operation="diff",
            rdf_added_data="<added> .",
            rdf_deleted_data="<removed> .",
            timestamp="2024-01-01T00:00:00Z",
        )
        event = RDFChangeEventBuilder.build(config)

        assert event.entity_id == "Q42"
        assert event.rev_id == 123
        assert event.operation == "diff"
        assert event.rdf_added_data is not None
        assert event.rdf_added_data.data == "<added> ."
        assert event.rdf_deleted_data is not None
        assert event.rdf_deleted_data.data == "<removed> ."

    def test_build_import_event(self):
        """Test building an import event."""
        config = RDFChangeEventBuilder.EventConfig(
            entity_id="Q42",
            rev_id=123,
            operation="import",
            rdf_added_data="<full rdf> .",
            rdf_deleted_data="",
            timestamp="2024-01-01T00:00:00Z",
        )
        event = RDFChangeEventBuilder.build(config)

        assert event.operation == "import"
        assert event.rdf_added_data is not None
        assert event.rdf_deleted_data is None

    def test_build_delete_event(self):
        """Test building a delete event."""
        config = RDFChangeEventBuilder.EventConfig(
            entity_id="Q42",
            rev_id=123,
            operation="delete",
            rdf_added_data="",
            rdf_deleted_data="",
            timestamp="2024-01-01T00:00:00Z",
        )
        event = RDFChangeEventBuilder.build(config)

        assert event.operation == "delete"
        assert event.rdf_added_data is None
        assert event.rdf_deleted_data is None

    def test_build_with_custom_domain(self):
        """Test building an event with custom domain."""
        config = RDFChangeEventBuilder.EventConfig(
            entity_id="Q42",
            rev_id=123,
            operation="diff",
            rdf_added_data="<test> .",
            rdf_deleted_data="",
            timestamp="2024-01-01T00:00:00Z",
            domain="test.wikidata.org",
        )
        event = RDFChangeEventBuilder.build(config)

        assert event.meta["domain"] == "test.wikidata.org"

    def test_build_with_request_id(self):
        """Test building an event with custom request ID."""
        config = RDFChangeEventBuilder.EventConfig(
            entity_id="Q42",
            rev_id=123,
            operation="diff",
            rdf_added_data="<test> .",
            rdf_deleted_data="",
            timestamp="2024-01-01T00:00:00Z",
            request_id="custom-request-123",
        )
        event = RDFChangeEventBuilder.build(config)

        assert event.meta["request_id"] == "custom-request-123"
