"""Integration tests for item description endpoints."""

import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_description_success(api_prefix: str) -> None:
    """Test getting item description for language."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Test Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/en"
        )
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_description_not_found(api_prefix: str) -> None:
    """Test getting item description for non-existent language returns 404."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Test Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/de"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_description_success(api_prefix: str) -> None:
    """Test updating item description for language."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Original Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Updated Description"},
            headers={"X-Edit-Summary": "update description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/en"
        )
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_description_creates_new(api_prefix: str) -> None:
    """Test updating item description creates new language if not exists."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Test Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/de",
            json={"language": "de", "value": "Neue Beschreibung"},
            headers={"X-Edit-Summary": "add german description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/de"
        )
        assert response.status_code == 200
        assert response.json()["value"] == "Neue Beschreibung"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_description_success(api_prefix: str) -> None:
    """Test deleting item description for language."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Description to Delete"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )
        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/de",
            json={"language": "de", "value": "German Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_description_not_found(api_prefix: str) -> None:
    """Test deleting non-existent item description is idempotent (returns 200)."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Test Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/descriptions/de",
            headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_item_description_via_post(api_prefix: str) -> None:
    """Test adding item description via POST endpoint."""
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

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Original Description"},
            headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
        )

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/descriptions/de",
            json={"language": "de", "value": "Neue Beschreibung"},
            headers={"X-Edit-Summary": "add german description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/de"
        )
        assert response.status_code == 200
        assert response.json()["value"] == "Neue Beschreibung"
