"""Integration tests for item label endpoints."""

import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_label_success(api_prefix: str) -> None:
    """Test getting item label for language."""
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
            json={"language": "en", "value": "Test Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_label_not_found(api_prefix: str) -> None:
    """Test getting item label for non-existent language returns 404."""
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
            json={"language": "en", "value": "Test Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/de")
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_label_multiple_languages(api_prefix: str) -> None:
    """Test getting item labels for multiple languages."""
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

        labels = [
            ("en", "Test English"),
            ("de", "Test German"),
            ("fr", "Test French"),
        ]
        for lang, value in labels:
            await client.put(
                f"{api_prefix}/entities/{entity_id}/labels/{lang}",
                json={"language": lang, "value": value},
                headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
            )

        for lang, expected in labels:
            response = await client.get(
                f"{api_prefix}/entities/{entity_id}/labels/{lang}"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["value"] == expected


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_label_success(api_prefix: str) -> None:
    """Test updating item label for language."""
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
            json={"language": "en", "value": "Original Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_label_creates_new(api_prefix: str) -> None:
    """Test updating item label creates new language if not exists."""
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
            json={"language": "en", "value": "Test Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/de",
            json={"language": "de", "value": "Neues Label"},
            headers={"X-Edit-Summary": "add german label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/de")
        assert response.status_code == 200
        assert response.json()["value"] == "Neues Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_label_entity_not_found(api_prefix: str) -> None:
    """Test updating item label for non-existent entity returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"{api_prefix}/entities/Q99999/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_label_success(api_prefix: str) -> None:
    """Test deleting item label for language."""
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
            json={"language": "en", "value": "Label to Delete"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )
        await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/de",
            json={"language": "de", "value": "German Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_label_not_found(api_prefix: str) -> None:
    """Test deleting non-existent item label is idempotent (returns 200)."""
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
            json={"language": "en", "value": "Test Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/labels/de",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_label_entity_not_found(api_prefix: str) -> None:
    """Test deleting item label for non-existent entity returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"{api_prefix}/entities/Q99999/labels/en",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_item_label_via_post(api_prefix: str) -> None:
    """Test adding item label via POST endpoint."""
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
            json={"language": "en", "value": "Original Label"},
            headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
        )

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/labels/de",
            json={"language": "de", "value": "Neues Label"},
            headers={"X-Edit-Summary": "add german label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/de")
        assert response.status_code == 200
        assert response.json()["value"] == "Neues Label"
