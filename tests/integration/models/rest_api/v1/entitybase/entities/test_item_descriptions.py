"""Integration tests for item description endpoints."""

import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_description_success(api_prefix: str) -> None:
    """Test getting item description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70008",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
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

        response = await client.get(f"{api_prefix}/entities/Q70008/descriptions/en")
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_description_not_found(api_prefix: str) -> None:
    """Test getting item description for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70009",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
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

        response = await client.get(f"{api_prefix}/entities/Q70009/descriptions/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_description_success(api_prefix: str) -> None:
    """Test updating item description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70010",
        type="item",
        descriptions={"en": {"value": "Original Description"}},
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
            f"{api_prefix}/entities/Q70010/descriptions/en",
            json={"language": "en", "value": "Updated Description"},
            headers={"X-Edit-Summary": "update description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/Q70010/descriptions/en")
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_description_creates_new(api_prefix: str) -> None:
    """Test updating item description creates new language if not exists."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70011",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
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
            f"{api_prefix}/entities/Q70011/descriptions/de",
            json={"language": "de", "value": "Neue Beschreibung"},
            headers={"X-Edit-Summary": "add german description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/Q70011/descriptions/de")
        assert response.status_code == 200
        assert response.json()["value"] == "Neue Beschreibung"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_description_success(api_prefix: str) -> None:
    """Test deleting item description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70012",
        type="item",
        descriptions={
            "en": {"value": "Description to Delete"},
            "de": {"value": "German Description"},
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
            f"{api_prefix}/entities/Q70012/descriptions/en",
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

    entity_data = EntityCreateRequest(
        id="Q70013",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
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
            f"{api_prefix}/entities/Q70013/descriptions/de",
            headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_item_description_via_post(api_prefix: str) -> None:
    """Test adding item description via POST endpoint."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70021",
        type="item",
        descriptions={"en": {"value": "Original Description"}},
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

        response = await client.post(
            f"{api_prefix}/entities/Q70021/descriptions/de",
            json={"language": "de", "value": "Neue Beschreibung"},
            headers={"X-Edit-Summary": "add german description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/Q70021/descriptions/de")
        assert response.status_code == 200
        assert response.json()["value"] == "Neue Beschreibung"
