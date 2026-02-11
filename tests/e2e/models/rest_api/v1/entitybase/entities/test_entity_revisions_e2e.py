"""E2E tests for entity revision operations."""

import pytest
import sys

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_specific_revision(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Get a specific revision of an entity."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Revision Test"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]
    revision_id = 1

    # Get specific revision
    response = await client.get(
        f"{e2e_base_url}/entities/{entity_id}/revision/{revision_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data or "revision" in data


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_revision_json_format(
    e2e_api_client, e2e_base_url, api_prefix
) -> None:
    from models.rest_api.main import app

    """E2E test: Get JSON representation of a specific revision."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "JSON Test"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]
    revision_id = 1

    # Get revision as JSON
    response = await client.get(
        f"{e2e_base_url}/entities/{entity_id}/revision/{revision_id}/json"
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data or "revision" in data


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_revision_ttl_format(
    e2e_api_client, e2e_base_url, api_prefix
) -> None:
    from models.rest_api.main import app

    """E2E test: Get Turtle (TTL) representation of a specific revision."""
    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "TTL Test"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]
    revision_id = 1

    # Get revision as TTL
    response = await client.get(
        f"{e2e_base_url}/entities/{entity_id}/revision/{revision_id}/ttl"
    )
    assert response.status_code == 200
    ttl_data = response.text
    assert "@prefix" in ttl_data or "@PREFIX" in ttl_data
    assert entity_id in ttl_data
