"""Integration tests for item alias endpoints."""

import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_success(api_prefix: str) -> None:
    """Test getting item aliases for language."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Alias 1"}, {"value": "Alias 2"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert "Alias 1" in data
        assert "Alias 2" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_not_found(api_prefix: str) -> None:
    """Test getting item aliases for non-existent language returns 404."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Test Alias"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_multiple(api_prefix: str) -> None:
    """Test getting multiple item aliases for language."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Alias 1"}, {"value": "Alias 2"}, {"value": "Alias 3"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_replace(api_prefix: str) -> None:
    """Test updating item aliases replaces existing ones."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Old Alias 1"}, {"value": "Old Alias 2"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "New Alias 1"}, {"value": "New Alias 2"}],
            headers={"X-Edit-Summary": "replace aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hashes" in data
        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert response.status_code == 200
        aliases = response.json()
        assert len(aliases) == 2
        assert "New Alias 1" in aliases
        assert "New Alias 2" in aliases


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_add(api_prefix: str) -> None:
    """Test updating item aliases creates new if not exists."""
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
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Test Item"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Alias 1"}, {"value": "Alias 2"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hashes" in data
        assert len(data["hashes"]) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_clear(api_prefix: str) -> None:
    """Test updating item aliases with empty list clears them."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Alias 1"}, {"value": "Alias 2"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[],
            headers={"X-Edit-Summary": "clear aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hashes" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_aliases_success(api_prefix: str) -> None:
    """Test deleting all item aliases for language."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Alias 1"}, {"value": "Alias 2"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )
        await client.put(
            f"{api_prefix}/entities/{entity_id}/aliases/de",
            json=[{"value": "Alias DE"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            headers={"X-Edit-Summary": "delete english aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_aliases_not_found(api_prefix: str) -> None:
    """Test deleting non-existent item aliases is idempotent (returns 200)."""
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
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Test Alias"}],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/aliases/de",
            headers={"X-Edit-Summary": "delete german aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
