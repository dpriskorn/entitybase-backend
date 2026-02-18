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

    entity_data = {
        "id": "Q90010",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Locked"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_locked": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=locked")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == "Q90010" for e in entities)

        logger.info("✓ Query locked entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_semi_protected_entities(api_prefix: str) -> None:
    """Query should return semi-protected items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90011",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Protected"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_semi_protected": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=semi_protected")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == "Q90011" for e in entities)

        logger.info("✓ Query semi-protected entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_archived_entities(api_prefix: str) -> None:
    """Query should return archived items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90012",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Archived"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_archived": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=archived")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == "Q90012" for e in entities)

        logger.info("✓ Query archived entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_dangling_entities(api_prefix: str) -> None:
    """Query should return dangling items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90013",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Dangling"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_dangling": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=dangling")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == "Q90013" for e in entities)

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
        # Create some test entities
        await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Item"}},
            },
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        await client.post(
            f"{api_prefix}/entities/lexemes",
            json={
                "type": "lexeme",
                "lemmas": {"en": {"language": "en", "value": "test"}},
                "lexicalCategory": "Q1084",
                "language": "Q1860",
            },
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

    entity_data = {
        "id": "Q90014",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_locked": True, "edit_type": "lock-added"},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=lock-added")
        assert response.status_code == 200
        result = response.json()
        entities = result["entities"]
        assert any(e["entity_id"] == "Q90014" for e in entities)

        logger.info("✓ Query by edit_type works")
