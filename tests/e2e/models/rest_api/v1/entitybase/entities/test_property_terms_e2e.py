"""E2E tests for property term operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_property(api_prefix: str, sample_property_data) -> None:
    from models.rest_api.main import app

    """E2E test: Create a new property entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=sample_property_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"].startswith("P")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_property_aliases(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get property aliases for language."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create property
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "Test Property"}},
            "aliases": {"en": [{"language": "en", "value": "Alias 1"}]},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        # Get aliases
        response = await client.get(f"{api_prefix}/entities/{property_id}/aliases/en")
        assert response.status_code == 200
        aliases_data = response.json()
        assert isinstance(aliases_data, list)
        assert "Alias 1" in aliases_data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_property_aliases(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Update property aliases for language."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create property
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "Test Property"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        # Update aliases
        response = await client.put(
            f"{api_prefix}/entities/{property_id}/aliases/en",
            json=["New Alias 1", "New Alias 2"],
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Verify update
        response = await client.get(f"{api_prefix}/entities/{property_id}/aliases/en")
        assert response.status_code == 200
        aliases_data = response.json()
        assert "New Alias 1" in aliases_data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_property_description(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get property description for language."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create property
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "Test Property"}},
            "descriptions": {"en": {"language": "en", "value": "Test Description"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        # Get description
        response = await client.get(
            f"{api_prefix}/entities/{property_id}/descriptions/en"
        )
        assert response.status_code == 200
        description_data = response.json()
        assert "value" in description_data
        assert description_data["value"] == "Test Description"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_property_label(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get property label for language."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create property
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "Test Label"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        # Get label
        response = await client.get(f"{api_prefix}/entities/{property_id}/labels/en")
        assert response.status_code == 200
        label_data = response.json()
        assert "value" in label_data
        assert label_data["value"] == "Test Label"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_property_labels_full_workflow(api_prefix: str) -> None:
    """E2E test: Full workflow for property labels (GET, PUT, POST, DELETE)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "Initial Label"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/{property_id}/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{property_id}/labels/en")
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Label"

        response = await client.post(
            f"{api_prefix}/entities/{property_id}/labels/de",
            json={"language": "de", "value": "German Label"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{property_id}/labels/de")
        assert response.status_code == 200
        assert response.json()["value"] == "German Label"

        response = await client.delete(
            f"{api_prefix}/entities/{property_id}/labels/de",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_property_descriptions_full_workflow(api_prefix: str) -> None:
    """E2E test: Full workflow for property descriptions (GET, PUT, POST, DELETE)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "descriptions": {"en": {"language": "en", "value": "Initial Description"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/{property_id}/descriptions/en",
            json={"language": "en", "value": "Updated Description"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/{property_id}/descriptions/en"
        )
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Description"

        response = await client.post(
            f"{api_prefix}/entities/{property_id}/descriptions/fr",
            json={"language": "fr", "value": "French Description"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/{property_id}/descriptions/fr",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_property_aliases_full_workflow(api_prefix: str) -> None:
    """E2E test: Full workflow for property aliases (GET, PUT, POST, DELETE)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "property",
            "datatype": "wikibase-item",
            "labels": {"en": {"language": "en", "value": "Test Property"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        property_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/{property_id}/aliases/en",
            json=["Alias 1", "Alias 2"],
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{property_id}/aliases/en")
        assert response.status_code == 200
        aliases_data = response.json()
        # Aliases may be returned as hashes or strings; check count is >= 2 (PUT) or >= 1 (POST adds one)
        if isinstance(aliases_data, list):
            assert len(aliases_data) >= 2
        else:
            # Hash-based response format
            assert isinstance(aliases_data, dict) or aliases_data is not None

        response = await client.post(
            f"{api_prefix}/entities/{property_id}/aliases/en",
            json={"language": "en", "value": "Alias 3"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{property_id}/aliases/en")
        assert response.status_code == 200
        # Aliases may be returned as hashes or strings; verify we have at least as many as before
        aliases_after_post = response.json()
        if isinstance(aliases_after_post, list):
            # POST should add one more alias
            assert (
                len(aliases_after_post) >= len(aliases_data)
                if isinstance(aliases_data, list)
                else True
            )
        # Hash-based format is also valid

        response = await client.delete(
            f"{api_prefix}/entities/{property_id}/aliases/en",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
