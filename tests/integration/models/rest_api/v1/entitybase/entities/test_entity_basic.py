import logging

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_check() -> None:
    """Test that health check endpoint returns OK
    This does not test all buckets work"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["s3"] == "connected"
        assert data["vitess"] == "connected"
        logger.info("✓ Health check passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_item() -> None:
    """Test creating a new empty item"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/v1/entitybase/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        entity_id = result["data"]["entity_id"]
        assert entity_id.startswith("Q")
        assert result["data"]["revision_id"] == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item() -> None:
    """Test retrieving an entity"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            "/v1/entitybase/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        response = await client.get(f"/v1/entitybase/entities/{entity_id}")
        assert response.status_code == 200

        result = response.json()
        assert result["id"] == entity_id
        assert result["rev_id"] == 1
        logger.info("✓ Entity retrieval passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_item_already_exists() -> None:
    """Test that creating an item with existing ID fails with 409"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/entities/items",
            json={
                "id": "Q99998",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            "/v1/entitybase/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 409
        assert "already exists" in response.json().get("message", "")

        logger.info("✓ GET with existing entity correctly returns 409")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_history() -> None:
    """Test retrieving entity history"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            "/v1/entitybase/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        await client.put(
            f"/v1/entitybase/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated Test Entity"},
            headers={"X-Edit-Summary": "update entity", "X-User-ID": "0"},
        )

        response = await client.get(f"/v1/entitybase/entities/{entity_id}/revisions")
        assert response.status_code == 200

        history = response.json()
        assert len(history) == 2
        assert history[0]["revision_id"] == 2
        assert history[1]["revision_id"] == 1
        assert "created_at" in history[0]
        assert "created_at" in history[1]
        logger.info("✓ Entity history retrieval passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_not_found() -> None:
    """Test that non-existent entities return 404"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/v1/entitybase/entities/Q88888")
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()
        logger.info("✓ 404 handling passed")
