"""E2E tests for entity sitelink operations."""

import pytest
import sys

sys.path.insert(0, "src")


@pytest.mark.e2e
def test_get_sitelink(e2e_api_client, e2e_base_url, sample_sitelink) -> None:
    """E2E test: Get a single sitelink for an entity."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Sitelink Test"}},
        "sitelinks": {"enwiki": sample_sitelink},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get sitelink
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}/sitelinks/enwiki")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert data["title"] == "Test Article"


@pytest.mark.e2e
def test_add_sitelink(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Add a new sitelink for an entity."""
    # Create entity
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Add sitelink
    sitelink_data = {"site": "enwiki", "title": "New Article", "badges": []}
    response = await client.post(
        f"{e2e_base_url}/entities/{entity_id}/sitelinks/enwiki",
        json=sitelink_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code in [200, 201]

    # Verify addition
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}/sitelinks/enwiki")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Article"


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_update_sitelink(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Update an existing sitelink for an entity."""
    # Create entity with sitelink
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Sitelink Update Test"}},
        "sitelinks": {"enwiki": {"site": "enwiki", "title": "Old Title", "badges": []}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Update sitelink
    update_data = {"site": "enwiki", "title": "Updated Title", "badges": []}
    response = await client.put(
        f"{e2e_base_url}/entities/{entity_id}/sitelinks/enwiki",
        json=update_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify update
    response = await client.get(f"{e2e_base_url}/entities/{entity_id}/sitelinks/enwiki")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_delete_sitelink(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Delete a sitelink from an entity."""
    # Create entity with sitelink
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Sitelink Delete Test"}},
        "sitelinks": {"enwiki": {"site": "enwiki", "title": "To Delete", "badges": []}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Delete sitelink
    response = await client.delete(
        f"{e2e_base_url}/entities/{entity_id}/sitelinks/enwiki",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code in [200, 204]
