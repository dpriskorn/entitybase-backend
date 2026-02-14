"""Unit tests for ttl_dump_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

from models.workers.ttl_dumps.ttl_dump_worker import (
    TtlDumpWorker,
)
from models.workers.dump_types import EntityDumpRecord


class TestTtlDumpWorker:
    """Unit tests for ttl_dump_worker."""

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = TtlDumpWorker()
        assert worker.worker_id is not None
        assert worker.running is False
        assert worker.vitess_client is None
        assert worker.s3_client is None
        assert worker.converter is None

    @pytest.mark.asyncio
    async def test_lifespan_initialization(self):
        """Test lifespan context manager initializes clients."""
        mock_vitess_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_converter = MagicMock()
        mock_property_registry = MagicMock()

        worker = TtlDumpWorker()

        with (
            patch(
                "models.workers.ttl_dumps.ttl_dump_worker.VitessClient",
                return_value=mock_vitess_client,
            ),
            patch(
                "models.workers.ttl_dumps.ttl_dump_worker.MyS3Client",
                return_value=mock_s3_client,
            ),
            patch(
                "models.workers.ttl_dumps.ttl_dump_worker.EntityConverter",
                return_value=mock_converter,
            ),
            patch(
                "models.workers.ttl_dumps.ttl_dump_worker.PropertyRegistry",
            ) as mock_registry_class,
        ):
            mock_registry_class.load_from_directory.return_value = (
                mock_property_registry
            )

            async with worker.lifespan():
                assert worker.vitess_client is not None
                assert worker.s3_client is not None
                assert worker.converter is not None

    @pytest.mark.asyncio
    async def test_health_check_running(self):
        """Test health check returns healthy when running."""
        worker = TtlDumpWorker()
        worker.running = True

        response = worker.health_check()
        assert response.status == "healthy"
        assert response.worker_id is not None

    @pytest.mark.asyncio
    async def test_health_check_stopped(self):
        """Test health check returns unhealthy when stopped."""
        worker = TtlDumpWorker()
        worker.running = False

        response = worker.health_check()
        assert response.status == "unhealthy"

    def test_calculate_seconds_until_next_run(self):
        """Test calculation of seconds until next run."""
        worker = TtlDumpWorker()

        with patch(
            "models.workers.ttl_dumps.ttl_dump_worker.settings"
        ) as mock_settings:
            mock_settings.ttl_dump_schedule = "0 3 * * *"
            with patch(
                "models.workers.ttl_dumps.ttl_dump_worker.datetime"
            ) as mock_datetime:
                now = datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
                target = datetime(2025, 1, 16, 3, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = now
                mock_datetime.time.side_effect = lambda h, m, s: datetime(
                    2025, 1, 1, h, m, s
                ).time()
                mock_datetime.combine.side_effect = lambda d, t: datetime.combine(
                    d, t
                ).replace(tzinfo=timezone.utc)
                mock_datetime.timedelta = timedelta

                seconds = worker._calculate_seconds_until_next_run()
                assert seconds > 0

    @pytest.mark.asyncio
    async def test_fetch_all_entities(self):
        """Test fetching all entities."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("Q1", 100, 1),
            ("Q2", 200, 2),
        ]

        mock_vitess_client = MagicMock()
        mock_vitess_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_vitess_client.cursor.__exit__ = MagicMock(return_value=False)

        worker = TtlDumpWorker()
        worker.vitess_client = mock_vitess_client

        entities = await worker._fetch_all_entities()

        assert len(entities) == 2
        assert entities[0].entity_id == "Q1"
        assert entities[0].internal_id == 100
        assert entities[0].revision_id == 1

    @pytest.mark.asyncio
    async def test_fetch_entities_for_week(self):
        """Test fetching entities updated within a week."""
        week_start = datetime(2025, 1, 8, 0, 0, 0, tzinfo=timezone.utc)
        week_end = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)

        mock_cursor = MagicMock()
        call_count = [0]

        def mock_fetchall():
            call_count[0] += 1
            if call_count[0] == 1:
                return [("Q1", 100, 1)]
            else:
                return [(1, 100, datetime(2025, 1, 10, 0, 0, 0, tzinfo=timezone.utc))]

        mock_cursor.fetchall.side_effect = mock_fetchall
        mock_cursor.execute = MagicMock()

        mock_vitess_client = MagicMock()
        mock_vitess_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_vitess_client.cursor.__exit__ = MagicMock(return_value=False)

        with patch(
            "models.workers.ttl_dumps.ttl_dump_worker.settings"
        ) as mock_settings:
            mock_settings.ttl_dump_batch_size = 1000

            worker = TtlDumpWorker()
            worker.vitess_client = mock_vitess_client

            entities = await worker._fetch_entities_for_week(week_start, week_end)

            assert len(entities) == 1
            assert entities[0].updated_at is not None

    def test_generate_checksum(self):
        """Test checksum generation."""
        import tempfile

        worker = TtlDumpWorker()

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write("test content")
            f.flush()
            from pathlib import Path

            checksum = worker._generate_checksum(Path(f.name))

            assert len(checksum) == 64  # SHA256 hex length
            assert all(c in "0123456789abcdef" for c in checksum)

    @pytest.mark.asyncio
    async def test_fetch_and_convert_entity_success(self):
        """Test successful entity fetch and conversion."""
        record = EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)

        mock_revision_data = MagicMock()
        mock_revision_data.revision = {
            "id": "Q1",
            "type": "item",
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "sitelinks": {},
            "claims": [],
        }

        mock_s3_client = MagicMock()
        mock_s3_client.read_revision.return_value = mock_revision_data

        mock_converter = MagicMock()
        mock_converter.convert_to_turtle = MagicMock()

        worker = TtlDumpWorker()
        worker.s3_client = mock_s3_client
        worker.converter = mock_converter

        data = await worker._fetch_and_convert_entity(record, MagicMock())
        assert data is not None
        mock_converter.convert_to_turtle.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_and_convert_entity_failure(self):
        """Test entity fetch and conversion with error."""
        record = EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)

        mock_s3_client = MagicMock()
        mock_s3_client.read_revision.side_effect = Exception("S3 error")

        worker = TtlDumpWorker()
        worker.s3_client = mock_s3_client

        data = await worker._fetch_and_convert_entity(record, MagicMock())
        assert data is None
