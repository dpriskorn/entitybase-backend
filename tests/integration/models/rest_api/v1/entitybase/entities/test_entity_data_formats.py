"""Integration tests for entity data formats (JSON, Turtle)."""

import logging

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_entity_data_json() -> None:
    """Test getting entity data in JSON format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/v1/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        await client.put(
            f"/v1/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Test Entity"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.get(f"/v1/entities/{entity_id}.json")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == entity_id
        assert "labels" in data
        logger.info("✓ Entity JSON retrieval passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_entity_data_turtle() -> None:
    """Test getting entity data in Turtle format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/v1/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        response = await client.get(f"/v1/entities/{entity_id}.ttl")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/turtle"
        logger.info("✓ Entity Turtle retrieval passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_entity_json_revision() -> None:
    """Test getting entity revision in JSON format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/v1/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        await client.put(
            f"/v1/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Test Entity"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.get(
            f"/v1/entities/{entity_id}/revision/1/json"
        )
        assert response.status_code == 200

        data = response.json()
        assert "labels" in data
        logger.info("✓ Entity JSON revision retrieval passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_entity_revision_not_found() -> None:
    """Test that non-existent revision returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/v1/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        response = await client.get(
            f"/v1/entities/{entity_id}/revision/999/json"
        )
        assert response.status_code == 404
        logger.info("✓ Non-existent revision returns 404")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_entity_json_revision_not_found() -> None:
    """Test that non-existent entity revision returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/v1/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        response = await client.get(
            f"/v1/entities/{entity_id}/revision/999/ttl"
        )
        assert response.status_code == 404
        logger.info("✓ Non-existent TTL revision returns 404")
