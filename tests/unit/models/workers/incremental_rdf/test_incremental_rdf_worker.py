"""Unit tests for incremental_rdf_worker and rdf_change_builder."""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from models.data.infrastructure.stream.consumer import EntityChangeEventData
from models.workers.incremental_rdf.rdf_change_builder import (
    EventConfig,
    RDFChangeEvent,
    RDFChangeEventBuilder,
    RDFDataField,
)
from models.workers.incremental_rdf.incremental_rdf_worker import (
    IncrementalRDFWorker,
)


class TestIncrementalRDFWorker:
    """Unit tests for IncrementalRDFWorker class."""

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = IncrementalRDFWorker(worker_id="test-worker", worker_enabled=False)
        assert worker.worker_id == "test-worker"
        assert worker.worker_enabled is False
        assert worker.vitess_client is None
        assert worker.s3_client is None
        assert worker.consumer is None
        assert worker.producer is None

    def test_get_kafka_brokers_empty(self):
        """Test getting kafka brokers when not configured."""
        with patch(
            "models.workers.incremental_rdf.incremental_rdf_worker.settings"
        ) as mock_settings:
            mock_settings.kafka_bootstrap_servers = None
            worker = IncrementalRDFWorker(worker_enabled=False)
            brokers = worker._get_kafka_brokers()
            assert brokers == []

    def test_get_kafka_brokers_with_servers(self):
        """Test getting kafka brokers when configured."""
        with patch(
            "models.workers.incremental_rdf.incremental_rdf_worker.settings"
        ) as mock_settings:
            mock_settings.kafka_bootstrap_servers = "broker1:9092, broker2:9092"
            worker = IncrementalRDFWorker(worker_enabled=False)
            brokers = worker._get_kafka_brokers()
            assert brokers == ["broker1:9092", "broker2:9092"]

    @pytest.mark.asyncio
    async def test_lifespan_disabled_worker(self):
        """Test lifespan when worker is disabled."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        async with worker.lifespan():
            pass

    @pytest.mark.asyncio
    async def test_process_message_invalid_no_entity_id(self):
        """Test processing message with missing entity_id."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        message = EntityChangeEventData(
            id="",
            rev=123,
            from_rev=None,
            type="update",
            at="2024-01-01T00:00:00Z",
            user="test",
            summary="test",
        )
        await worker.process_message(message)

    @pytest.mark.asyncio
    async def test_process_message_invalid_no_revision_id(self):
        """Test processing message with missing revision_id."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        message = EntityChangeEventData(
            id="Q42",
            rev=0,
            from_rev=None,
            type="update",
            at="2024-01-01T00:00:00Z",
            user="test",
            summary="test",
        )
        await worker.process_message(message)

    @pytest.mark.asyncio
    async def test_process_message_delete(self):
        """Test processing delete message."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        worker.producer = MagicMock()
        worker.producer.publish = AsyncMock()

        message = EntityChangeEventData(
            id="Q42",
            rev=123,
            from_rev=None,
            type="delete",
            at="2024-01-01T00:00:00Z",
            user="test",
            summary="test",
        )
        await worker.process_message(message)

        worker.producer.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_no_consumer(self):
        """Test run when consumer is not initialized."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        await worker.run()

    def test_compute_diff_and_rdf_import_operation(self):
        """Test compute diff for import operation (no old data)."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        operation, rdf_added = worker._compute_diff_and_rdf(
            "Q42", None, {"entity": {"id": "Q42"}}
        )
        assert operation == "import"
        assert rdf_added == ""

    def test_compute_diff_and_rdf_diff_operation(self):
        """Test compute diff for diff operation (with old data)."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        with patch.object(
            worker, "_compute_rdf_diff", return_value="<diff> ."
        ) as mock_diff:
            operation, rdf_added = worker._compute_diff_and_rdf(
                "Q42",
                {"entity": {"id": "Q42"}},
                {"entity": {"id": "Q42"}},
            )
            assert operation == "diff"
            mock_diff.assert_called_once()

    def test_convert_to_entity_data_success(self):
        """Test converting dict to EntityData."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        entity_data = {
            "entity": {
                "id": "Q42",
                "type": "item",
                "labels": {"en": {"value": "Test"}},
                "descriptions": {},
                "aliases": {},
                "statements": [],
                "sitelinks": {},
            }
        }
        result = worker._convert_to_entity_data(entity_data)
        assert result is not None
        assert result.id == "Q42"
        assert result.type == "item"

    def test_convert_to_entity_data_with_empty_entity_key(self):
        """Test converting dict with empty entity key to EntityData."""
        worker = IncrementalRDFWorker(worker_enabled=False)
        result = worker._convert_to_entity_data({})
        assert result is not None
        assert result.id == ""


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
        config = EventConfig(
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
        config = EventConfig(
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
        config = EventConfig(
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
        config = EventConfig(
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
        config = EventConfig(
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
