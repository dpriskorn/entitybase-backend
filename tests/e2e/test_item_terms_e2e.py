import pytest


@pytest.mark.e2e
def test_item_labels_full_workflow(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Create item, update labels, get labels, delete labels."""
    base_url = e2e_base_url

    create_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Initial Label"}},
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

    response = e2e_api_client.get(f"{base_url}/entities/items/{entity_id}/labels/en")
    assert response.status_code == 200
    label_data = response.json()
    assert label_data["value"] == "Initial Label"

    response = e2e_api_client.put(
        f"{base_url}/entities/items/{entity_id}/labels/en",
        json={"language": "en", "value": "Updated Label"},
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = e2e_api_client.get(f"{base_url}/entities/items/{entity_id}/labels/en")
    assert response.status_code == 200
    label_data = response.json()
    assert label_data["value"] == "Updated Label"

    response = e2e_api_client.delete(
        f"{base_url}/entities/items/{entity_id}/labels/en",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200


@pytest.mark.e2e
def test_item_descriptions_full_workflow(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Create item, update descriptions, get descriptions, delete descriptions."""
    base_url = e2e_base_url

    create_data = {
        "type": "item",
        "descriptions": {"en": {"language": "en", "value": "Initial Description"}},
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

    response = e2e_api_client.get(
        f"{base_url}/entities/items/{entity_id}/descriptions/en"
    )
    assert response.status_code == 200
    description_data = response.json()
    assert description_data["value"] == "Initial Description"

    response = e2e_api_client.put(
        f"{base_url}/entities/items/{entity_id}/descriptions/en",
        json={"language": "en", "value": "Updated Description"},
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = e2e_api_client.get(
        f"{base_url}/entities/items/{entity_id}/descriptions/en"
    )
    assert response.status_code == 200
    description_data = response.json()
    assert description_data["value"] == "Updated Description"

    response = e2e_api_client.delete(
        f"{base_url}/entities/items/{entity_id}/descriptions/en",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    entity_data = response.json()
    entity_id = entity_data["id"]
    assert entity_id.startswith("Q")

    response = e2e_api_client.get(
        f"{base_url}/entities/items/{entity_id}/descriptions/en"
    )
    assert response.status_code == 200
    description_data = response.json()
    assert description_data["value"] == "Initial Description"

    response = e2e_api_client.put(
        f"{base_url}/entities/items/{entity_id}/descriptions/en",
        json={"language": "en", "value": "Updated Description"},
    )
    assert response.status_code == 200

    response = e2e_api_client.get(
        f"{base_url}/entities/items/{entity_id}/descriptions/en"
    )
    assert response.status_code == 200
    description_data = response.json()
    assert description_data["value"] == "Updated Description"

    response = e2e_api_client.delete(
        f"{base_url}/entities/items/{entity_id}/descriptions/en"
    )
    assert response.status_code == 200


@pytest.mark.e2e
def test_item_aliases_full_workflow(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Create item, update aliases, get aliases."""
    base_url = e2e_base_url

    create_data = {
        "type": "item",
        "aliases": {"en": [{"language": "en", "value": "Alias 1"}]},
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

    response = e2e_api_client.get(f"{base_url}/entities/items/{entity_id}/aliases/en")
    assert response.status_code == 200
    aliases_data = response.json()
    assert len(aliases_data) == 1
    assert "Alias 1" in aliases_data

    response = e2e_api_client.put(
        f"{base_url}/entities/items/{entity_id}/aliases/en",
        json=["Alias 1", "Alias 2", "Alias 3"],
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = e2e_api_client.get(f"{base_url}/entities/items/{entity_id}/aliases/en")
    assert response.status_code == 200
    aliases_data = response.json()
    assert len(aliases_data) == 3
