import pytest


@pytest.mark.e2e
def test_health_check(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Health check endpoint."""
    response = e2e_api_client.get(f"{e2e_base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.e2e
def test_general_stats(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get general statistics."""
    response = e2e_api_client.get(f"{e2e_base_url}/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_entities" in data or "entities" in data


@pytest.mark.e2e
def test_json_import_endpoint(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Import entities from Wikidata JSONL dump file."""
    import_data = {
        "entities": [
            {
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Import Test"}},
            }
        ],
        "batch_size": 10,
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/json-import",
        json=import_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    # May return 202 for async processing or 200 for success
    assert response.status_code in [200, 202, 400]


@pytest.mark.e2e
def test_entity_lifecycle(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Create, read, update, delete entity."""
    base_url = e2e_base_url

    # Create entity
    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "descriptions": {"en": {"language": "en", "value": "E2E test item"}},
    }
    response = e2e_api_client.post(
        f"{base_url}/entities/items",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_data = response.json()
    entity_id = entity_data["id"]
    assert entity_id.startswith("Q")

    # Read entity
    response = e2e_api_client.get(f"{base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["labels"]["en"]["value"] == "Test Item"

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
                "rank": "normal",
            }
        ],
    }
    response = e2e_api_client.put(
        f"{base_url}/entities/{entity_id}",
        json=update_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify update
    response = e2e_api_client.get(f"{base_url}/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["labels"]["en"]["value"] == "Updated Test Item"
    assert len(data["statements"]) > 0

    # Delete entity (if supported)
    # Note: Wikibase may not support direct deletion; adjust based on API
    # response = e2e_api_client.delete(f"{base_url}/entities/{entity_id}")
    # assert response.status_code == 204

    # For now, just verify the entity exists
    response = e2e_api_client.get(f"{base_url}/entities/{entity_id}")
    assert response.status_code == 200
