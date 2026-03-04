"""Integration tests for optimistic locking (CAS) functionality."""

import logging

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_without_base_revision_always_succeeds(api_prefix: str) -> None:
    """Test that updating without base revision (default 0) always succeeds.

    This ensures backward compatibility - edits without X-Base-Revision-ID
    header should work as before without any CAS check.
    """
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]
        assert create_response.json()["data"]["revision_id"] == 1

        first_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "First Update"},
            headers={"X-Edit-Summary": "first update", "X-User-ID": "0"},
        )
        assert first_update.status_code == 200
        assert "hash" in first_update.json()

        second_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Second Update"},
            headers={"X-Edit-Summary": "second update", "X-User-ID": "0"},
        )
        assert second_update.status_code == 200
        assert "hash" in second_update.json()

        logger.info("✓ Update without base revision succeeds (backward compatible)")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_with_correct_base_revision_succeeds(api_prefix: str) -> None:
    """Test that updating with correct base revision succeeds."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]
        assert create_response.json()["data"]["revision_id"] == 1

        update_response = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={
                "X-Edit-Summary": "update with correct base",
                "X-User-ID": "0",
                "X-Base-Revision-ID": "1",
            },
        )
        assert update_response.status_code == 200
        assert "hash" in update_response.json()

        logger.info("✓ Update with correct base revision succeeds")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_with_stale_base_revision_returns_409(api_prefix: str) -> None:
    """Test that updating with stale base revision returns 409 Conflict."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]
        assert create_response.json()["data"]["revision_id"] == 1

        first_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "First Update"},
            headers={"X-Edit-Summary": "first update", "X-User-ID": "0"},
        )
        assert first_update.status_code == 200
        assert "hash" in first_update.json()

        second_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Stale Update"},
            headers={
                "X-Edit-Summary": "stale update",
                "X-User-ID": "0",
                "X-Base-Revision-ID": "1",
            },
        )
        assert second_update.status_code == 409
        assert "Conflict" in second_update.json().get("message", "")
        assert "modified" in second_update.json().get("message", "").lower()

        logger.info("✓ Update with stale base revision returns 409 Conflict")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_after_stale_revision_succeeds(api_prefix: str) -> None:
    """Test that updating after a stale revision error succeeds.

    Scenario:
    1. Create entity at revision 1
    2. First update succeeds (revision becomes 2)
    3. Second update with stale base_revision_id=1 fails with 409
    4. Third update without base_revision_id succeeds
    """
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]
        assert create_response.json()["data"]["revision_id"] == 1

        first_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "First Update"},
            headers={"X-Edit-Summary": "first update", "X-User-ID": "0"},
        )
        assert first_update.status_code == 200

        stale_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Stale Update"},
            headers={
                "X-Edit-Summary": "stale update",
                "X-User-ID": "0",
                "X-Base-Revision-ID": "1",
            },
        )
        assert stale_update.status_code == 409

        third_update = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Third Update"},
            headers={"X-Edit-Summary": "third update", "X-User-ID": "0"},
        )
        assert third_update.status_code == 200

        logger.info("✓ Update after stale revision succeeds")
