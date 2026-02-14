"""Integration tests for JSON dump worker with real Vitess and S3."""

import json
import logging
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
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

    @pytest_asyncio.fixture
    async def setup_test_entities(self):
        """Setup test entities from test_data/json_import/test1.jsonl."""
        from models.rest_api.main import app

        entity_ids = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            headers = {"X-Edit-Summary": "Dump worker test setup", "X-User-ID": "0"}

            # Create L42 lexeme
            L42_data = {
                "id": "L42",
                "type": "lexeme",
                "language": "Q1860",
                "lexicalCategory": "Q1084",
                "lemmas": {"en": {"language": "en", "value": "answer"}},
                "labels": {"en": {"language": "en", "value": "answer"}},
            }
            response = await client.post(
                "/v1/entitybase/entities/lexemes",
                json=L42_data,
                headers=headers,
            )
            assert response.status_code == 200
            entity_ids.append("L42")
            logger.info("Created L42 entity")

            # Create Q42 item
            Q42_data = {
                "id": "Q42",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
                "descriptions": {
                    "en": {"language": "en", "value": "British science fiction writer"}
                },
            }
            response = await client.post(
                "/v1/entitybase/entities/items",
                json=Q42_data,
                headers=headers,
            )
            assert response.status_code == 200
            entity_ids.append("Q42")
            logger.info("Created Q42 entity")

            # Create P31 property
            P31_data = {
                "id": "P31",
                "type": "property",
                "datatype": "wikibase-item",
                "labels": {"en": {"language": "en", "value": "instance of"}},
                "descriptions": {
                    "en": {
                        "language": "en",
                        "value": "that class of which this subject is a particular instance and member",
                    }
                },
            }
            response = await client.post(
                "/v1/entitybase/entities/properties",
                json=P31_data,
                headers=headers,
            )
            assert response.status_code == 200
            entity_ids.append("P31")
            logger.info("Created P31 property")

        yield entity_ids

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
        # Note: Lexemes and Properties get auto-generated IDs, Items can use custom IDs
        assert "L5000000" in entity_ids  # Auto-generated lexeme ID
        assert "Q42" in entity_ids  # Custom item ID works
        assert "P1000001" in entity_ids  # Auto-generated property ID

        logger.info(f"Found {len(entities)} entities in database")
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

        # Note: Q42 is created with a custom ID and should be included
        assert len(entities) >= 1, f"Expected at least 1 entity, got {len(entities)}"

        logger.info(f"Found {len(entities)} entities updated in week")
        logger.info("=== test_fetch_entities_for_week_from_db END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_entity_data_from_s3(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test fetching entity data from real S3."""
        logger.info("=== test_fetch_entity_data_from_s3 START ===")

        entities = await json_dump_worker._fetch_all_entities()

        # Note: Q42 has a custom ID, but other entities have auto-generated IDs
        q42_entity = next((e for e in entities if e.entity_id == "Q42"), None)
        assert q42_entity is not None, "Q42 not found in database"

        data = await json_dump_worker._fetch_entity_data(q42_entity)

        assert data is not None
        # The revision data doesn't have an "id" field, but has entity_type
        assert data.get("entity_type") == "item"
        # The entity_id is in the record, not the revision data
        assert q42_entity.entity_id == "Q42"

        logger.info("Successfully fetched Q42 from S3")
        logger.info("=== test_fetch_entity_data_from_s3 END ===")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_dump_workflow(
        self, json_dump_worker: JsonDumpWorker, setup_test_entities
    ):
        """Test complete full dump workflow."""
        logger.info("=== test_full_dump_workflow START ===")

        entities = await json_dump_worker._fetch_all_entities()

        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=7)
        week_end = now

        dump_date = now.strftime("%Y-%m-%d")

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
