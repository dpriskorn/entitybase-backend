"""E2E tests for property term operations."""

import pytest
import sys

sys.path.insert(0, "src")


@pytest.mark.e2e
def test_create_property(e2e_api_client, e2e_base_url, sample_property_data) -> None:
    """E2E test: Create a new property entity."""
    response = await client.post(
        f"{e2e_base_url}/entities/properties",
        json=sample_property_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"].startswith("P")
    assert "datatype" in data


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_property_aliases(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Get property aliases for language."""
    # Create property
    create_data = {
        "type": "property",
        "datatype": "wikibase-item",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
        "aliases": {"en": [{"language": "en", "value": "Alias 1"}]},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/properties",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    property_id = response.json()["id"]

    # Get aliases
    response = await client.get(
        f"{e2e_base_url}/entities/properties/{property_id}/aliases/en"
    )
    assert response.status_code == 200
    aliases_data = response.json()
    assert isinstance(aliases_data, list)
    assert "Alias 1" in aliases_data


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_update_property_aliases(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Update property aliases for language."""
    # Create property
    create_data = {
        "type": "property",
        "datatype": "wikibase-item",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/properties",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    property_id = response.json()["id"]

    # Update aliases
    response = await client.put(
        f"{e2e_base_url}/entities/properties/{property_id}/aliases/en",
        json=["New Alias 1", "New Alias 2"],
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify update
    response = await client.get(
        f"{e2e_base_url}/entities/properties/{property_id}/aliases/en"
    )
    assert response.status_code == 200
    aliases_data = response.json()
    assert "New Alias 1" in aliases_data


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_property_description(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Get property description for language."""
    # Create property
    create_data = {
        "type": "property",
        "datatype": "wikibase-item",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
        "descriptions": {"en": {"language": "en", "value": "Test Description"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/properties",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    property_id = response.json()["id"]

    # Get description
    response = await client.get(
        f"{e2e_base_url}/entities/properties/{property_id}/descriptions/en"
    )
    assert response.status_code == 200
    description_data = response.json()
    assert "value" in description_data
    assert description_data["value"] == "Test Description"


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_property_label(e2e_api_client, e2e_base_url, api_prefix) -> None:
    from models.rest_api.main import app

    """E2E test: Get property label for language."""
    # Create property
    create_data = {
        "type": "property",
        "datatype": "wikibase-item",
        "labels": {"en": {"language": "en", "value": "Test Label"}},
    }
    response = await client.post(
        f"{e2e_base_url}/entities/properties",
        json=create_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    property_id = response.json()["id"]

    # Get label
    response = await client.get(
        f"{e2e_base_url}/entities/properties/{property_id}/labels/en"
    )
    assert response.status_code == 200
    label_data = response.json()
    assert "value" in label_data
    assert label_data["value"] == "Test Label"
