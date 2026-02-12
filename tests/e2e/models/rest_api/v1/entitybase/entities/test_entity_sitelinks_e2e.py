"""E2E tests for entity sitelink operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_sitelink(api_prefix: str, sample_sitelink) -> None:
    """E2E test: Get a single sitelink for an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Sitelink Test"}},
            "sitelinks": {"enwiki": sample_sitelink},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get sitelink
        response = await client.get(f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert data["title"] == "Test Article"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_add_sitelink(api_prefix: str, sample_item_data) -> None:
    """E2E test: Add a new sitelink for an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Add sitelink
        sitelink_data = {"site": "enwiki", "title": "New Article", "badges": []}
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki",
            json=sitelink_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 201]

        # Verify addition
        response = await client.get(f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Article"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_sitelink(api_prefix: str) -> None:
    """E2E test: Update an existing sitelink for an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with sitelink
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Sitelink Update Test"}},
            "sitelinks": {"enwiki": {"site": "enwiki", "title": "Old Title", "badges": []}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Update sitelink
        update_data = {"site": "enwiki", "title": "Updated Title", "badges": []}
        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki",
            json=update_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Verify update
        response = await client.get(f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_delete_sitelink(api_prefix: str) -> None:
    """E2E test: Delete a sitelink from an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with sitelink
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Sitelink Delete Test"}},
            "sitelinks": {"enwiki": {"site": "enwiki", "title": "To Delete", "badges": []}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Delete sitelink
        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 204]
