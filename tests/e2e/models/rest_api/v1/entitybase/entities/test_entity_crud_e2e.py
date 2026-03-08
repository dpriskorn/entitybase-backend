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
        response = await client.get(
            f"{api_prefix}/entities?status=locked&limit=5&offset=0"
        )
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
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert "data" in data
        assert (
            "hashes" in data["data"]["revision"] or "labels" in data["data"]["revision"]
        )


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_json_export(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get entity data in JSON format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

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
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

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
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated History Test"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}/revisions")
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        assert len(history) >= 2


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_revert_entity(api_prefix: str) -> None:
    """E2E test: Revert an entity to a previous revision."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        # First update
        put_response1 = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "First revision"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert put_response1.status_code == 200

        # Second update
        put_response2 = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Second revision"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert put_response2.status_code == 200

        revisions_response = await client.get(
            f"{api_prefix}/entities/{entity_id}/revisions"
        )
        assert revisions_response.status_code == 200
        revisions = revisions_response.json()
        assert len(revisions) >= 2, (
            f"Expected at least 2 revisions, got {len(revisions)}"
        )
        first_rev_id = revisions[1]["revision_id"]

        revert_response = await client.post(
            f"{api_prefix}/entities/{entity_id}/revert",
            json={"to_revision_id": first_rev_id},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert revert_response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_create_and_update_entity(api_prefix: str) -> None:
    """E2E test: Create entity and update its data."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_entity_revision_count(api_prefix: str) -> None:
    """E2E test: Verify revision count increments on updates."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]
        initial_rev = create_response.json()["data"]["revision_id"]

        await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Update 1"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["rev_id"] == initial_rev + 1
