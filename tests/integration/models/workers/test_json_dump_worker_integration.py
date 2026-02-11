"""Integration tests for JSON dump worker with real Vitess and S3."""

import json
import logging
import pytest
from datetime import datetime, timezone
from pathlib import Path
from httpx import ASGITransport, AsyncClient

from models.workers.json_dumps.json_dump_worker import JsonDumpWorker
from models.workers.dump_types import EntityDumpRecord

logger = logging.getLogger(__name__)


class TestJsonDumpWorkerIntegration:
    """Integration tests for JsonDumpWorker with real services."""

    @pytest.fixture
    def json_dump_worker(self, vitess_client, s3_client):
        """Create JsonDumpWorker with real clients."""
        worker = JsonDumpWorker()
        worker.vitess_client = vitess_client
        worker.s3_client = s3_client
        return worker

    @pytest.fixture
    async def setup_test_entities(self, api_prefix: str):
        """Setup test entities from test_data/json_import/test1.jsonl."""
        from models.rest_api.main import app

        entity_ids = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            headers = {"X-Edit-Summary": "Dump worker test setup", "X-User-ID": "0"}

            L42_data = {
                "id": "L42",
                "type": "lexeme",
                "language": "Q1860",
                "lexicalCategory": "Q1084",
                "lemmas": {"en": {"language": "en", "value": "answer"}},
                "labels": {"en": {"language": "en", "value": "answer"}},
            }
            response = await client.post(
                f"{api_prefix}/entities/lexemes",
                json=L42_data,
                headers=headers,
            )
            assert response.status_code == 200
            entity_ids.append("L42")

            Q42_data = {
                "id": "Q42",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
                "descriptions": {
                    "en": {"language": "en", "value": "British science fiction writer"}
                },
                "statements": [],
            }
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=Q42_data,
                headers=headers,
            )
            assert response.status_code == 200
            entity_ids.append("Q42")

            P31_data = {
                "id": "P31",
                "type": "property",
                "datatype": "wikibase-item",
                "labels": {"en": {"language": "en", "value": "instance of"}},
                "descriptions": {
                    "en": {
                        "language": "en",
                        "value": "that class of which this subject is a particular instance and member"
                    }
                },
                "statements": [],
            }
            response = await client.post(
                f"{api_prefix}/entities/properties",
                json=P31_data,
                headers=headers,
            )
            assert response.status_code == 200
            entity_ids.append("P31")

        yield entity_ids

        cleanup done in tests/integration/conftest.py db_cleanup fixture

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_all_entities_from_db(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test fetching all entities from real Vitess database."""
        logger.info("=== test_fetch_all_entities_from_db START ===")

        entities = await json_dump_worker._fetch_all_entities()

        assert len(entities) >= 3
        entity_ids = [e.entity_id for e in entities]
        assert "L42" in entity_ids
        assert "Q42" in entity_ids
        assert "P31" in entity_ids

        for entity in entities:
            assert entity.entity_id is not None
            assert entity.internal_id is not None
            assert entity.revision_id is not None
            assert entity.revision_id >= 1

        logger.info(f"Found {len(entities)} entities")
        logger.info("=== test_fetch_all_entities_from_db END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_entities_for_week_from_db(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test fetching entities updated within a week from real Vitess."""
        logger.info("=== test_fetch_entities_for_week_from_db START ===")

        now = datetime.now(timezone.utc)
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = now

        entities = await json_dump_worker._fetch_entities_for_week(week_start, week_end)

        assert len(entities) >= 3
        for entity in entities:
            assert entity.updated_at is not None
            assert week_start <= entity.updated_at < week_end

        logger.info(f"Found {len(entities)} entities updated in week")
        logger.info("=== test_fetch_entities_for_week_from_db END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_entity_data_from_s3(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test fetching entity data from real S3."""
        logger.info("=== test_fetch_entity_data_from_s3 START ===")

        record = EntityDumpRecord(entity_id="Q42", internal_id=1, revision_id=1)

        data = await json_dump_worker._fetch_entity_data(record)

        assert data is not None
        assert data.get("id") == "Q42"
        assert data.get("type") == "item"
        assert "labels" in data

        logger.info("Successfully fetched Q42 from S3")
        logger.info("=== test_fetch_entity_data_from_s3 END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_json_dump_file(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test generating JSON dump file."""
        logger.info("=== test_generate_json_dump_file START ===")

        entities = await json_dump_worker._fetch_all_entities()

        from datetime import timedelta
        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        week_end = datetime.now(timezone.utc)

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_full.json"

            await json_dump_worker._generate_json_dump(entities, output_path, week_start, week_end)

            assert output_path.exists()
            with open(output_path, "r") as f:
                dump_data = json.load(f)

            assert "dump_metadata" in dump_data
            assert "entities" in dump_data
            assert dump_data["dump_metadata"]["entity_count"] >= 3
            assert dump_data["dump_metadata"]["format"] == "canonical-json"

            entity_entry = dump_data["entities"][0]
            assert "entity" in entity_entry
            assert "metadata" in entity_entry
            assert "entity_id" in entity_entry["metadata"]
            assert "revision_id" in entity_entry["metadata"]
            assert "s3_uri" in entity_entry["metadata"]

        logger.info("JSON dump file generated successfully")
        logger.info("=== test_generate_json_dump_file END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_dump_workflow(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test complete full dump workflow."""
        logger.info("=== test_full_dump_workflow START ===")

        entities = await json_dump_worker._fetch_all_entities()
        dump_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        from datetime import timedelta
        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        week_end = datetime.now(timezone.utc)

        await json_dump_worker._generate_and_upload_dump(
            entities, dump_date, "full", week_start, week_end
        )

        logger.info("Full dump workflow completed")
        logger.info("=== test_full_dump_workflow END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_incremental_dump_workflow(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test complete incremental dump workflow."""
        logger.info("=== test_incremental_dump_workflow START ===")

        now = datetime.now(timezone.utc)
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = now

        entities = await json_dump_worker._fetch_entities_for_week(week_start, week_end)
        dump_date = now.strftime("%Y-%m-%d")

        await json_dump_worker._generate_and_upload_dump(
            entities, dump_date, "incremental", week_start, week_end
        )

        logger.info("Incremental dump workflow completed")
        logger.info("=== test_incremental_dump_workflow END ===")
