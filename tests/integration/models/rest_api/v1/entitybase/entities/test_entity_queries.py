import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_locked_entities(api_prefix: str) -> None:
    """Query should return locked items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=locked")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == entity_id for e in entities)

        logger.info("✓ Query locked entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_semi_protected_entities(api_prefix: str) -> None:
    """Query should return semi-protected items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/semi-protect",
            headers={"X-Edit-Summary": "semi-protect entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=semi_protected")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == entity_id for e in entities)

        logger.info("✓ Query semi-protected entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_archived_entities(api_prefix: str) -> None:
    """Query should return archived items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "archive entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=archived")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == entity_id for e in entities)

        logger.info("✓ Query archived entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_dangling_entities(api_prefix: str) -> None:
    """Query should return dangling items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]
        logger.info(f"Created entity: {create_response.json()}")

        response = await client.get(f"{api_prefix}/entities?status=dangling")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        logger.info(f"Entities returned: {entities}")
        assert any(e.get("entity_id") == entity_id for e in entities)

        logger.info("✓ Query dangling entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_entities_by_type(api_prefix: str) -> None:
    """Test listing entities by type"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test item", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/lexemes",
            headers={"X-Edit-Summary": "create lexeme", "X-User-ID": "0"},
        )

        # List items
        response = await client.get(f"{api_prefix}/entities?entity_type=item")
        assert response.status_code == 200
        result = response.json()
        assert "entities" in result
        assert "count" in result
        assert result["count"] > 0
        for entity in result["entities"]:
            assert "entity_id" in entity
            assert "head_revision_id" in entity
            assert entity["entity_id"].startswith("Q")

        # List lexemes
        response = await client.get(f"{api_prefix}/entities?entity_type=lexeme")
        assert response.status_code == 200
        result = response.json()
        assert result["count"] > 0
        for entity in result["entities"]:
            assert entity["entity_id"].startswith("L")

        logger.info("✓ List entities by type works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_by_edit_type(api_prefix: str) -> None:
    """Query should return entities filtered by edit_type"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock-added", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=lock-added")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == entity_id for e in entities)

        logger.info("✓ Query by edit_type works")
