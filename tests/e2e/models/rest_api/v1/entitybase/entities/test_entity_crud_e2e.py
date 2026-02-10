"""E2E tests for entity CRUD operations and format exports."""

import pytest
import sys

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_list_entities_all(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: List all entities without filters."""
    response = await client.get(f"{e2e_base_url}/entities")
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_list_entities_with_type_filter(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: List entities filtered by type."""
    response = await client.get(f"{e2e_base_url}/entities?entity_type=item&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_list_entities_with_limit_offset(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: List entities with limit and offset pagination."""
    response = await client.get(f"{e2e_base_url}/entities?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data or isinstance(data, list)


@pytest.mark.e2e
def test_get_single_entity(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get a single entity by ID."""
    # Create entity first
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get entity
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entity_id
    assert "labels" in data
    assert data["labels"]["en"]["value"] == "Test Item"


@pytest.mark.e2e
def test_get_entity_json_export(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get entity data in JSON format."""
    # Create entity first
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get JSON export
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}.json")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entity_id


@pytest.mark.e2e
def test_get_entity_ttl_export(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get entity data in Turtle format."""
    # Create entity first
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get TTL export
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}.ttl")
    assert response.status_code == 200
    ttl_data = response.text
    assert "@prefix" in ttl_data or "@PREFIX" in ttl_data
    assert entity_id in ttl_data


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_get_entity_history(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: Get revision history for an entity."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "History Test"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Update to create second revision
    response = await client.put(
        f"{e2e_base_url}/entities/items/{entity_id}/labels/en",
        json={"language": "en", "value": "Updated History Test"},
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get history
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}/history")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) >= 2


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_revert_entity(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: Revert entity to a previous revision."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Original Label"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]
    original_rev = response.json()["rev_id"]

    # Update label
    response = await client.put(
        f"{e2e_base_url}/entities/items/{entity_id}/labels/en",
        json={"language": "en", "value": "Modified Label"},
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Revert to original
    revert_data = {"revision_id": original_rev}
    response = await client.post(
        f"{e2e_base_url}/entities/{entity_id}/revert",
        json=revert_data,
        headers={"X-Edit-Summary": "Revert E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_delete_entity(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: Delete an entity."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Be Deleted"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Delete entity
    response = await client.delete(
        f"{e2e_base_url}/entities/{entity_id}",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    # May return 204 or 200 depending on implementation
    assert response.status_code in [200, 204]

    # Verify deletion
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code in [404, 410]  # Not found or gone
