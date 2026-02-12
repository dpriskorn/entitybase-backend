"""E2E tests for entity revision operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_specific_revision(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get a specific revision of an entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Revision Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]
        revision_id = 1

        # Get specific revision
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/revision/{revision_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or "revision" in data or "id" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_revision_json_format(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get JSON representation of a specific revision."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "JSON Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]
        revision_id = response.json().get("rev_id", 1)

        # Get revision as JSON
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/revision/{revision_id}/json"
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or "id" in data or "labels" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_revision_ttl_format(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get Turtle (TTL) representation of a specific revision."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "TTL Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]
        revision_id = response.json().get("rev_id", 1)

        # Get revision as TTL
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/revision/{revision_id}/ttl"
        )
        assert response.status_code == 200
        ttl_data = response.text
        assert "@prefix" in ttl_data.lower() or "prefix" in ttl_data.lower() or entity_id in ttl_data
