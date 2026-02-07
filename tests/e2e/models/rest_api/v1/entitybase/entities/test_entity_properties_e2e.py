"""E2E tests for entity property operations."""

import pytest


@pytest.mark.e2e
def test_get_entity_properties(
    e2e_api_client, e2e_base_url, sample_item_with_statements
) -> None:
    """E2E test: Get list of unique property IDs for an entity."""
    # Create entity with statements
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_with_statements,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get properties
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}/properties")
    assert response.status_code == 200
    data = response.json()
    assert "properties" in data or isinstance(data, list)
    if isinstance(data, dict) and "properties" in data:
        assert "P31" in data["properties"] or len(data["properties"]) > 0


@pytest.mark.e2e
def test_add_property_to_entity(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Add claims for a single property to an entity."""
    # Create entity
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Add property claim
    claim_data = {
        "property": {"id": "P31", "data_type": "wikibase-item"},
        "value": {"type": "value", "content": "Q5"},
        "rank": "normal",
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/{entity_id}/properties/P31",
        json=claim_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code in [200, 201]


@pytest.mark.e2e
def test_get_entity_property_hashes(
    e2e_api_client, e2e_base_url, sample_item_with_statements
) -> None:
    """E2E test: Get entity property hashes for specified properties."""
    # Create entity with statements
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_with_statements,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get property hashes
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}/properties/P31")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) or "hashes" in data


@pytest.mark.e2e
def test_get_entity_property_hashes_alternative_endpoint(
    e2e_api_client, e2e_base_url, sample_item_with_statements
) -> None:
    """E2E test: Get statement hashes using alternative endpoint."""
    # Create entity with statements
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_with_statements,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get property hashes via alternative endpoint
    response = e2e_api_client.get(f"{e2e_base_url}/entity/{entity_id}/properties/P31")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) or "hashes" in data
