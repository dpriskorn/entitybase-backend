"""E2E tests for entity CRUD operations and format exports."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_list_entities_all(api_prefix: str) -> None:
    """E2E test: List entities with status filter."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?status=locked")
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data or isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_list_entities_with_type_filter(api_prefix: str) -> None:
    """E2E test: List entities filtered by type."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?entity_type=item&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data or isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_list_entities_with_limit_offset(api_prefix: str) -> None:
    """E2E test: List entities with limit and offset pagination."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?status=locked&limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data or isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_single_entity(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get a single entity by ID."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity first
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get entity
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert "data" in data
        assert "labels" in data["data"]["revision"]
        assert data["data"]["revision"]["labels"]["en"]["value"] == "Test Item"


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_json_export(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get entity data in JSON format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity first
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get JSON export
        response = await client.get(f"{api_prefix}/entities/{entity_id}.json")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == entity_id


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_ttl_export(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get entity data in Turtle format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity first
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get TTL export
        response = await client.get(f"{api_prefix}/entities/{entity_id}.ttl")
        assert response.status_code == 200
        ttl_data = response.text
        assert "@prefix" in ttl_data or "@PREFIX" in ttl_data
        assert entity_id in ttl_data


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_history(api_prefix: str) -> None:
    """E2E test: Get revision history for an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "History Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Update to create second revision
        response = await client.put(
            f"{api_prefix}/entities/items/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated History Test"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Get history
        response = await client.get(f"{api_prefix}/entities/{entity_id}/history")
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        assert len(history) >= 2


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_revert_entity(api_prefix: str) -> None:
    """E2E test: Revert entity to a previous revision."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Original Label"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]
        original_rev = response.json()["rev_id"]

        # Update label
        response = await client.put(
            f"{api_prefix}/entities/items/{entity_id}/labels/en",
            json={"language": "en", "value": "Modified Label"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Revert to original
        revert_data = {"to_revision_id": original_rev}
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/revert",
            json=revert_data,
            headers={"X-Edit-Summary": "Revert E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_delete_entity(api_prefix: str) -> None:
    """E2E test: Delete an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "To Be Deleted"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Delete entity
        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        # May return 204 or 200 depending on implementation
        assert response.status_code in [200, 204]

        # Verify deletion
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code in [404, 410]  # Not found or gone
