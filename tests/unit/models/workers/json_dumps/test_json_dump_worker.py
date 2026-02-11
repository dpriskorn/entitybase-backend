"""Unit tests for json_dump_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

from models.workers.json_dumps.json_dump_worker import (
    JsonDumpWorker,
)
from models.workers.dump_types import EntityDumpRecord


class TestJsonDumpWorker:
    """Unit tests for json_dump_worker."""

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = JsonDumpWorker()
        assert worker.worker_id is not None
        assert worker.running is False
        assert worker.vitess_client is None
        assert worker.s3_client is None

    @pytest.mark.asyncio
    async def test_lifespan_initialization(self):
        """Test lifespan context manager initializes clients."""
        mock_vitess_client = MagicMock()
        mock_s3_client = MagicMock()

        worker = JsonDumpWorker()

        with patch(
            "models.workers.json_dumps.json_dump_worker.VitessClient",
            return_value=mock_vitess_client,
        ), patch(
            "models.workers.json_dumps.json_dump_worker.MyS3Client",
            return_value=mock_s3_client,
        ):
            async with worker.lifespan():
                assert worker.vitess_client is not None
                assert worker.s3_client is not None

    @pytest.mark.asyncio
    async def test_health_check_running(self):
        """Test health check returns healthy when running."""
        worker = JsonDumpWorker()
        worker.running = True

        response = worker.health_check()
        assert response.status == "healthy"
        assert response.worker_id is not None

    @pytest.mark.asyncio
    async def test_health_check_stopped(self):
        """Test health check returns unhealthy when stopped."""
        worker = JsonDumpWorker()
        worker.running = False

        response = worker.health_check()
        assert response.status == "unhealthy"

    def test_calculate_seconds_until_next_run(self):
        """Test calculation of seconds until next run."""
        worker = JsonDumpWorker()

        with patch(
            "models.workers.json_dumps.json_dump_worker.settings"
        ) as mock_settings:
            mock_settings.json_dump_schedule = "0 2 * * *"
            with patch(
                "models.workers.json_dumps.json_dump_worker.datetime"
            ) as mock_datetime:
                now = datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
                target = datetime(2025, 1, 16, 2, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = now
                mock_datetime.time.side_effect = lambda h, m, s: datetime(
                    2025, 1, 1, h, m, s
                ).time()
                mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t).replace(tzinfo=timezone.utc)
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

        worker = JsonDumpWorker()
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
            "models.workers.json_dumps.json_dump_worker.settings"
        ) as mock_settings:
            mock_settings.json_dump_batch_size = 1000

            worker = JsonDumpWorker()
            worker.vitess_client = mock_vitess_client

            entities = await worker._fetch_entities_for_week(week_start, week_end)

            assert len(entities) == 1
            assert entities[0].updated_at is not None

    def test_generate_checksum(self):
        """Test checksum generation."""
        import tempfile
        worker = JsonDumpWorker()

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write("test content")
            f.flush()
            from pathlib import Path
            checksum = worker._generate_checksum(Path(f.name))

            assert len(checksum) == 64  # SHA256 hex length
            assert all(c in "0123456789abcdef" for c in checksum)

    @pytest.mark.asyncio
    async def test_fetch_entity_data_success(self):
        """Test successful entity data fetch."""
        record = EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)

        mock_revision_data = MagicMock()
        mock_revision_data.revision = {"id": "Q1", "type": "item"}

        mock_s3_client = MagicMock()
        mock_s3_client.read_revision.return_value = mock_revision_data

        worker = JsonDumpWorker()
        worker.s3_client = mock_s3_client

        data = await worker._fetch_entity_data(record)
        assert data is not None
        assert data["id"] == "Q1"

    @pytest.mark.asyncio
    async def test_fetch_entity_data_failure(self):
        """Test entity data fetch with error."""
        record = EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)

        mock_s3_client = MagicMock()
        mock_s3_client.read_revision.side_effect = Exception("S3 error")

        worker = JsonDumpWorker()
        worker.s3_client = mock_s3_client

        data = await worker._fetch_entity_data(record)
        assert data is None

    @pytest.mark.asyncio
    async def test_start_disabled_worker(self):
        """Test worker exits when json_dump_enabled is False."""
        worker = JsonDumpWorker()

        with patch(
            "models.workers.json_dumps.json_dump_worker.settings"
        ) as mock_settings:
            mock_settings.json_dump_enabled = False

            await worker.start()

            worker.running = False

    @pytest.mark.asyncio
    async def test_start_loop_error_recovery(self):
        """Test worker handles exceptions and sleeps after error."""
        import asyncio
        from models.workers.json_dumps.json_dump_worker import JsonDumpWorker as WorkerClass
        from contextlib import asynccontextmanager

        worker = JsonDumpWorker()

        mock_sleep_calls = []

        async def mock_sleep(seconds):
            mock_sleep_calls.append(seconds)
            if len(mock_sleep_calls) == 1 and seconds == 300:
                worker.running = False

        @asynccontextmanager
        async def mock_lifespan(self):
            yield

        with patch("asyncio.sleep", side_effect=mock_sleep):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.json_dump_enabled = True

                with patch.object(WorkerClass, "lifespan", mock_lifespan):
                    with patch.object(worker, "_calculate_seconds_until_next_run", return_value=0.001):
                        with patch.object(WorkerClass, "run_weekly_dump", side_effect=Exception("Test error")):
                            await worker.start()

        assert 300 in mock_sleep_calls

    @pytest.mark.asyncio
    async def test_run_weekly_dump_no_full_entities(self):
        """Test worker skips full dump when no entities available."""
        worker = JsonDumpWorker()

        with patch.object(worker, "_fetch_all_entities", return_value=[]):
            with patch.object(worker, "_fetch_entities_for_week", return_value=[]):
                with patch.object(worker, "_generate_and_upload_dump") as mock_generate:
                    await worker.run_weekly_dump()

                    full_dump_call = [c for c in mock_generate.call_args_list if "full" in str(c)]
                    assert len(full_dump_call) == 0

    @pytest.mark.asyncio
    async def test_run_weekly_dump_no_incremental_entities(self):
        """Test worker skips incremental dump when no entities updated."""
        worker = JsonDumpWorker()

        entities = [EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)]
        with patch.object(worker, "_fetch_all_entities", return_value=entities):
            with patch.object(worker, "_fetch_entities_for_week", return_value=[]):
                with patch.object(worker, "_generate_and_upload_dump") as mock_generate:
                    await worker.run_weekly_dump()

                    incremental_call = [c for c in mock_generate.call_args_list if "incremental" in str(c)]
                    assert len(incremental_call) == 0

    @pytest.mark.asyncio
    async def test_generate_json_dump_structure(self):
        """Test generated JSON dump has correct structure."""
        import tempfile
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        worker.s3_client = mock_s3_client

        entities = [EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)]

        with patch.object(worker, "_fetch_entity_data", return_value={"id": "Q1", "type": "item"}):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.json_dump_compression = False
                mock_settings.json_dump_batch_size = 1000
                mock_settings.s3_dump_bucket = "test-bucket"

                with tempfile.TemporaryDirectory() as tmpdir:
                    from pathlib import Path
                    output_path = Path(tmpdir) / "test.json"

                    week_start = datetime.now(timezone.utc)
                    week_end = datetime.now(timezone.utc)

                    await worker._generate_json_dump(entities, output_path, week_start, week_end)

                    import json
                    with open(output_path, "r") as f:
                        dump_data = json.load(f)

                assert "dump_metadata" in dump_data
                assert "entities" in dump_data
                assert "generated_at" in dump_data["dump_metadata"]
                assert "time_range" in dump_data["dump_metadata"]
                assert "entity_count" in dump_data["dump_metadata"]
                assert "format" in dump_data["dump_metadata"]

    @pytest.mark.asyncio
    async def test_generate_json_dump_entity_format(self):
        """Test each entity in dump has correct format."""
        import tempfile
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        worker.s3_client = mock_s3_client

        entities = [EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)]

        with patch.object(worker, "_fetch_entity_data", return_value={"id": "Q1", "type": "item"}):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.s3_dump_bucket = "test-bucket"
                mock_settings.json_dump_batch_size = 1000
                mock_settings.json_dump_compression = False

                with tempfile.TemporaryDirectory() as tmpdir:
                    from pathlib import Path
                    output_path = Path(tmpdir) / "test.json"

                    week_start = datetime.now(timezone.utc)
                    week_end = datetime.now(timezone.utc)

                    await worker._generate_json_dump(entities, output_path, week_start, week_end)

                    import json
                    with open(output_path, "r") as f:
                        dump_data = json.load(f)

                    assert len(dump_data["entities"]) == 1
                    entity_entry = dump_data["entities"][0]
                    assert "entity" in entity_entry
                    assert "metadata" in entity_entry
                    assert "revision_id" in entity_entry["metadata"]
                    assert "entity_id" in entity_entry["metadata"]
                    assert "s3_uri" in entity_entry["metadata"]

    @pytest.mark.asyncio
    async def test_generate_json_dump_compression_enabled(self):
        """Test dump uses gzip when compression is enabled."""
        import tempfile
        import gzip
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        worker.s3_client = mock_s3_client

        entities = [EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)]

        with patch.object(worker, "_fetch_entity_data", return_value={"id": "Q1", "type": "item"}):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.json_dump_compression = True
                mock_settings.json_dump_batch_size = 1000
                mock_settings.s3_dump_bucket = "test-bucket"

                with tempfile.TemporaryDirectory() as tmpdir:
                    from pathlib import Path
                    output_path = Path(tmpdir) / "test.json.gz"

                    week_start = datetime.now(timezone.utc)
                    week_end = datetime.now(timezone.utc)

                    await worker._generate_json_dump(entities, output_path, week_start, week_end)

                    assert output_path.exists()

                    with gzip.open(output_path, "rt") as f:
                        import json
                        data = json.load(f)
                        assert "dump_metadata" in data

    @pytest.mark.asyncio
    async def test_generate_json_dump_compression_disabled(self):
        """Test dump uses plain JSON when compression is disabled."""
        import tempfile
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        worker.s3_client = mock_s3_client

        entities = [EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)]

        with patch.object(worker, "_fetch_entity_data", return_value={"id": "Q1", "type": "item"}):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.json_dump_compression = False
                mock_settings.json_dump_batch_size = 1000
                mock_settings.s3_dump_bucket = "test-bucket"

                with tempfile.TemporaryDirectory() as tmpdir:
                    from pathlib import Path
                    output_path = Path(tmpdir) / "test.json"

                    week_start = datetime.now(timezone.utc)
                    week_end = datetime.now(timezone.utc)

                    await worker._generate_json_dump(entities, output_path, week_start, week_end)

                    assert output_path.exists()

                    gz_path = Path(tmpdir) / "test.json.gz"
                    assert not gz_path.exists()

                    import json
                    with open(output_path, "r") as f:
                        data = json.load(f)
                        assert "dump_metadata" in data

    @pytest.mark.asyncio
    async def test_generate_json_dump_batch_processing(self):
        """Test dump processes entities in batches."""
        import tempfile
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        worker.s3_client = mock_s3_client

        entities = [
            EntityDumpRecord(entity_id=f"Q{i}", internal_id=i*100, revision_id=i)
            for i in range(1, 11)
        ]

        def mock_fetch(record):
            return {"id": record.entity_id, "type": "item"}

        with patch.object(worker, "_fetch_entity_data", side_effect=mock_fetch):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.json_dump_batch_size = 3
                mock_settings.json_dump_compression = False
                mock_settings.s3_dump_bucket = "test-bucket"

                with tempfile.TemporaryDirectory() as tmpdir:
                    from pathlib import Path
                    output_path = Path(tmpdir) / "test.json"

                    week_start = datetime.now(timezone.utc)
                    week_end = datetime.now(timezone.utc)

                    await worker._generate_json_dump(entities, output_path, week_start, week_end)

                    import json
                    with open(output_path, "r") as f:
                        data = json.load(f)

                    assert data["dump_metadata"]["entity_count"] == 10

    @pytest.mark.asyncio
    async def test_generate_json_dump_fetch_failure_handling(self):
        """Test failed entity fetches are excluded from dump."""
        import tempfile
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        worker.s3_client = mock_s3_client

        entities = [
            EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1),
            EntityDumpRecord(entity_id="Q2", internal_id=200, revision_id=2),
            EntityDumpRecord(entity_id="Q3", internal_id=300, revision_id=3),
        ]

        def mock_fetch(record):
            if record.entity_id == "Q2":
                raise Exception("Fetch failed")
            return {"id": record.entity_id, "type": "item"}

        with patch.object(worker, "_fetch_entity_data", side_effect=mock_fetch):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.s3_dump_bucket = "test-bucket"
                mock_settings.json_dump_batch_size = 1000
                mock_settings.json_dump_compression = False

                with tempfile.TemporaryDirectory() as tmpdir:
                    from pathlib import Path
                    output_path = Path(tmpdir) / "test.json"

                    week_start = datetime.now(timezone.utc)
                    week_end = datetime.now(timezone.utc)

                    await worker._generate_json_dump(entities, output_path, week_start, week_end)

                    import json
                    with open(output_path, "r") as f:
                        data = json.load(f)

                    assert data["dump_metadata"]["entity_count"] == 2
                    entity_ids = [e["metadata"]["entity_id"] for e in data["entities"]]
                    assert "Q1" in entity_ids
                    assert "Q2" not in entity_ids
                    assert "Q3" in entity_ids

    @pytest.mark.asyncio
    async def test_generate_and_upload_dump_metadata(self):
        """Test metadata file generation and upload."""
        import tempfile
        import json
        worker = JsonDumpWorker()

        mock_s3_client = MagicMock()
        mock_s3_client.connection_manager = MagicMock()
        mock_boto = MagicMock()
        mock_s3_client.connection_manager.boto_client = mock_boto
        worker.s3_client = mock_s3_client

        entities = [EntityDumpRecord(entity_id="Q1", internal_id=100, revision_id=1)]

        def mock_json_dump(data, f, **kwargs):
            """Mock json.dump to handle datetime objects."""
            from datetime import datetime as DT
            from collections.abc import Mapping

            class DateTimeEncoder(json.JSONEncoder):
                def default(self, o):
                    if isinstance(o, DT):
                        return o.isoformat()
                    return super().default(o)

            json.dump(data, f, cls=DateTimeEncoder, **kwargs)

        with patch.object(worker, "_fetch_entity_data", return_value={"id": "Q1", "type": "item"}):
            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.s3_dump_bucket = "test-bucket"
                mock_settings.json_dump_compression = False
                mock_settings.json_dump_generate_checksums = False
                mock_settings.json_dump_batch_size = 1000

                with patch("models.workers.json_dumps.json_dump_worker.json.dump", side_effect=mock_json_dump):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        from pathlib import Path
                        output_path = Path(tmpdir) / "test.json"

                        week_start = datetime.now(timezone.utc)
                        week_end = datetime.now(timezone.utc)

                        await worker._generate_and_upload_dump(entities, "2025-01-15", "full", week_start, week_end)

                    metadata_path = Path(tmpdir) / "metadata.json"
                    assert metadata_path.exists()

                    import json
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    assert metadata["dump_id"] == "2025-01-15"
                    assert metadata["entity_count"] == 1
                    assert metadata["format"] == "canonical-json"
                    assert metadata["dump_type"] == "full"

    @pytest.mark.asyncio
    async def test_upload_to_s3_with_checksum(self):
        """Test S3 upload includes checksum in metadata."""
        import tempfile
        worker = JsonDumpWorker()

        mock_boto = MagicMock()
        mock_s3_client = MagicMock()
        mock_s3_client.connection_manager = MagicMock()
        mock_s3_client.connection_manager.boto_client = mock_boto

        worker.s3_client = mock_s3_client

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write('{"test": "data"}')
            f.flush()
            from pathlib import Path
            filepath = Path(f.name)

            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.s3_dump_bucket = "test-bucket"
                mock_settings.json_dump_compression = False
                mock_settings.json_dump_generate_checksums = True

                checksum = worker._generate_checksum(filepath)

                await worker._upload_to_s3(filepath, "weekly/2025-01-15/full.json", checksum)

                mock_boto.upload_file.assert_called_once()
                call_args = mock_boto.upload_file.call_args

                assert call_args[0][1] == "test-bucket"
                assert call_args[0][2] == "weekly/2025-01-15/full.json"
                extra_args = call_args[1]["ExtraArgs"]
                assert "Metadata" in extra_args
                assert extra_args["Metadata"]["sha256"] == checksum

            Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_upload_to_s3_content_type(self):
        """Test S3 upload sets correct content type."""
        import tempfile
        import gzip
        worker = JsonDumpWorker()

        mock_boto = MagicMock()
        mock_s3_client = MagicMock()
        mock_s3_client.connection_manager = MagicMock()
        mock_s3_client.connection_manager.boto_client = mock_boto

        worker.s3_client = mock_s3_client

        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path

            json_path = Path(tmpdir) / "test.json"
            json_path.write_text('{"test": "data"}')

            gz_path = Path(tmpdir) / "test.json.gz"
            with gzip.open(gz_path, "wt") as f:
                f.write('{"test": "data"}')

            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.s3_dump_bucket = "test-bucket"
                mock_settings.json_dump_compression = False
                mock_settings.json_dump_generate_checksums = False

                await worker._upload_to_s3(json_path, "weekly/test.json", "")
                call_args = mock_boto.upload_file.call_args
                extra_args = call_args[1]["ExtraArgs"]
                assert extra_args["ContentType"] == "application/json"

            with patch("models.workers.json_dumps.json_dump_worker.settings") as mock_settings:
                mock_settings.s3_dump_bucket = "test-bucket"
                mock_settings.json_dump_compression = True
                mock_settings.json_dump_generate_checksums = False

                await worker._upload_to_s3(gz_path, "weekly/test.json.gz", "")
                call_args = mock_boto.upload_file.call_args
                extra_args = call_args[1]["ExtraArgs"]
                assert extra_args["ContentType"] == "application/gzip"
