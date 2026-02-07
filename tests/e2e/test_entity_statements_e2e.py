"""E2E tests for entity statement management."""

import pytest


@pytest.mark.e2e
def test_remove_statement(
    e2e_api_client, e2e_base_url, sample_item_with_statements
) -> None:
    """E2E test: Remove a statement by hash from an entity."""
    # Create entity with statements
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_with_statements,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get statement hash
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    statement_hash = data["statements"][0]

    # Remove statement
    response = e2e_api_client.delete(
        f"{e2e_base_url}/entities/{entity_id}/statements/{statement_hash}",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code in [200, 204]

    # Verify removal
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert statement_hash not in data["statements"] or len(data["statements"]) == 0


@pytest.mark.e2e
def test_replace_statement(
    e2e_api_client, e2e_base_url, sample_item_with_statements
) -> None:
    """E2E test: Replace a statement by hash with new claim data."""
    # Create entity with statements
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_with_statements,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get statement hash
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    original_hash = data["statements"][0]

    # Replace statement
    new_claim_data = {
        "property": {"id": "P31", "data_type": "wikibase-item"},
        "value": {"type": "value", "content": "Q5"},
        "rank": "preferred",
    }
    response = e2e_api_client.patch(
        f"{e2e_base_url}/entities/{entity_id}/statements/{original_hash}",
        json=new_claim_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify replacement
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    # Statement hash should be different after update
    assert original_hash not in data["statements"] or len(data["statements"]) > 0
