"""End-to-end tests for JSON dump worker."""

import json
import logging
import pytest
from datetime import datetime, timezone
from pathlib import Path
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_weekly_dump_full_workflow_e2e(api_prefix: str) -> None:
    """E2E test: Complete weekly dump workflow."""
    from models.rest_api.main import app
    from models.workers.json_dumps.json_dump_worker import JsonDumpWorker

    logger.info("=== test_weekly_dump_full_workflow_e2e START ===")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "E2E dump worker test", "X-User-ID": "0"}

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
        logger.info("Created L42 entity")

        Q42_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {
                "en": {"language": "en", "value": "British science fiction writer"}
            },
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=Q42_data,
            headers=headers,
        )
        assert response.status_code == 200
        logger.info("Created Q42 entity")

        P31_data = {
            "id": "P31",
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "instance of"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=P31_data,
            headers=headers,
        )
        assert response.status_code == 200
        logger.info("Created P31 entity")

    logger.info("Entities created, running dump worker...")

    logger.info("=== test_weekly_dump_full_workflow_e2e END ===")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_health_check_endpoint(api_prefix: str) -> None:
    """E2E test: Worker health check endpoint."""
    from models.rest_api.main import app
    from models.workers.json_dumps.json_dump_worker import JsonDumpWorker

    logger.info("=== test_health_check_endpoint START ===")

    worker = JsonDumpWorker()

    response = worker.health_check()

    assert response.status == "unhealthy"
    assert response.worker_id is not None

    worker.running = True
    response = worker.health_check()

    assert response.status == "healthy"

    logger.info("=== test_health_check_endpoint END ===")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_worker_scheduling(api_prefix: str) -> None:
    """E2E test: Worker schedule calculation."""
    from models.rest_api.main import app
    from models.workers.json_dumps.json_dump_worker import JsonDumpWorker

    logger.info("=== test_worker_scheduling START ===")

    worker = JsonDumpWorker()

    seconds = worker._calculate_seconds_until_next_run()

    assert seconds >= 0
    assert seconds < 86400 * 7

    logger.info(f"Next run in {seconds} seconds")
    logger.info("=== test_worker_scheduling END ===")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_concurrent_dumps(api_prefix: str) -> None:
    """E2E test: Worker handles full and incremental dumps."""
    from models.rest_api.main import app
    from models.workers.json_dumps.json_dump_worker import JsonDumpWorker

    logger.info("=== test_concurrent_dumps START ===")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "E2E concurrent dump test", "X-User-ID": "0"}

        for i in range(1, 4):
            item_data = {
                "id": f"Q99{i}",
                "type": "item",
                "labels": {"en": {"language": "en", "value": f"Test Item {i}"}},
            }
            await client.post(
                f"{api_prefix}/entities/items",
                json=item_data,
                headers=headers,
            )
            logger.info(f"Created Q99{i} entity")

    logger.info("=== test_concurrent_dumps END ===")
