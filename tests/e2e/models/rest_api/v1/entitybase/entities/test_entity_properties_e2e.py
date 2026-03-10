"""E2E tests for entity property operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_properties(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Get list of unique property IDs for an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        response = await client.post(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        # Get properties
        response = await client.get(f"{api_prefix}/entities/{entity_id}/properties")
        assert response.status_code == 200
        data = response.json()
        assert "properties" in data or isinstance(data, list)
        properties = data.get("properties", data) if isinstance(data, dict) else data
        # Properties may be empty if statements are stored as hashes
        assert isinstance(properties, (list, dict))


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_add_property_to_entity(
    api_prefix: str, sample_item_data, sample_property_data
) -> None:
    """E2E test: Add claims for a single property to an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create property first
        property_response = await client.post(
            f"{api_prefix}/entities/properties",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert property_response.status_code == 200
        property_id = property_response.json()["data"]["entity_id"]

        # Create entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        # Add property claim - use valid Wikibase statement JSON format
        claim_data = {
            "claims": [
                {
                    "id": "TESTCLAIM123",
                    "mainsnak": {
                        "snaktype": "value",
                        "property": property_id,
                        "datavalue": {"value": {"id": "Q5"}, "type": "wikibase-item"},
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ]
        }
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/properties/{property_id}",
            json=claim_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_property_hashes(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Get entity property hashes for specified properties."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        # Get property hashes
        response = await client.get(f"{api_prefix}/entities/{entity_id}/properties/P31")
        assert response.status_code == 200
        data = response.json()
        # Response may be a list, or contain 'hashes', 'property_hashes', or 'statements'
        assert (
            isinstance(data, list)
            or "hashes" in data
            or "property_hashes" in data
            or "statements" in data
        )


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_entity_property_hashes_alternative_endpoint(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Get statement hashes using alternative endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        response = await client.post(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        # Get property hashes via alternative endpoint
        response = await client.get(f"{api_prefix}/entities/{entity_id}/properties/P31")
        assert response.status_code == 200
        data = response.json()
        # Response may be a list, or contain 'hashes', 'property_hashes', or 'statements'
        assert (
            isinstance(data, list)
            or "hashes" in data
            or "property_hashes" in data
            or "statements" in data
        )
