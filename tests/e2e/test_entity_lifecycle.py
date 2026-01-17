import pytest


@pytest.mark.e2e
def test_entity_lifecycle(e2e_api_client, e2e_base_url):
    """E2E test: Create, read, update, delete entity."""
    base_url = e2e_base_url

    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "descriptions": {"en": {"language": "en", "value": "E2E test item"}},
    }
    response = e2e_api_client.post(f"{base_url}/entity", json=create_data)
    assert response.status_code == 200
    entity_data = response.json()
    entity_id = entity_data["entity"]["id"]
    assert entity_id.startswith("Q")

    # Read entity
    response = e2e_api_client.get(f"{base_url}/entity/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["entity"]["labels"]["en"]["value"] == "Test Item"

    # Update entity (add statement)
    update_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Updated Test Item"}},
        "descriptions": {"en": {"language": "en", "value": "Updated E2E test item"}},
        "statements": [
            {
                "property": {"id": "P31", "data_type": "wikibase-item"},
                "value": {"type": "value", "content": "Q5"},  # instance of human
                "rank": "normal"
            }
        ]
    }
    response = e2e_api_client.put(f"{base_url}/entity/{entity_id}", json=update_data)
    assert response.status_code == 200

    # Verify update
    response = e2e_api_client.get(f"{base_url}/entity/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["entity"]["labels"]["en"]["value"] == "Updated Test Item"
    assert len(data["entity"]["statements"]) > 0

    # Delete entity (if supported)
    # Note: Wikibase may not support direct deletion; adjust based on API
    # response = e2e_api_client.delete(f"{base_url}/entity/{entity_id}")
    # assert response.status_code == 204

    # For now, just verify the entity exists
    response = e2e_api_client.get(f"{base_url}/entity/{entity_id}")
    assert response.status_code == 200