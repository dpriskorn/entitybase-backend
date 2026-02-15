"""Integration tests for item alias endpoints."""

import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_success(api_prefix: str) -> None:
    """Test getting item aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70014",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q70014/aliases/en")
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

    entity_data = EntityCreateRequest(
        id="Q70015",
        type="item",
        aliases={"en": [{"value": "Test Alias"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q70015/aliases/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_multiple(api_prefix: str) -> None:
    """Test getting multiple item aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70016",
        type="item",
        aliases={
            "en": [{"value": "Alias 1"}, {"value": "Alias 2"}, {"value": "Alias 3"}]
        },
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q70016/aliases/en")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_replace(api_prefix: str) -> None:
    """Test updating item aliases replaces existing ones."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70017",
        type="item",
        aliases={"en": [{"value": "Old Alias 1"}, {"value": "Old Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/Q70017/aliases/en",
            json=["New Alias 1", "New Alias 2"],
            headers={"X-Edit-Summary": "replace aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hashes" in data
        response = await client.get(f"{api_prefix}/entities/Q70017/aliases/en")
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

    entity_data = EntityCreateRequest(
        id="Q70018",
        type="item",
        labels={"en": {"value": "Test Item"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/Q70018/aliases/en",
            json=["Alias 1", "Alias 2"],
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

    entity_data = EntityCreateRequest(
        id="Q70019",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/Q70019/aliases/en",
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

    entity_data = EntityCreateRequest(
        id="Q70022",
        type="item",
        aliases={
            "en": [{"value": "Alias 1"}, {"value": "Alias 2"}],
            "de": [{"value": "Alias DE"}],
        },
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/Q70022/aliases/en",
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

    entity_data = EntityCreateRequest(
        id="Q70023",
        type="item",
        aliases={"en": [{"value": "Test Alias"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/Q70023/aliases/de",
            headers={"X-Edit-Summary": "delete german aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
