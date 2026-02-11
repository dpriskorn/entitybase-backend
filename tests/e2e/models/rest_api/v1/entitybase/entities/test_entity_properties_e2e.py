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
            "/entities/items",
            json=sample_item_with_statements,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get properties
        response = await client.get(f"/entities/{entity_id}/properties")
        assert response.status_code == 200
        data = response.json()
        assert "properties" in data or isinstance(data, list)
        if isinstance(data, dict) and "properties" in data:
            assert "P31" in data["properties"] or len(data["properties"]) > 0


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_add_property_to_entity(api_prefix: str, sample_item_data) -> None:
    """E2E test: Add claims for a single property to an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            "/entities/items",
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
        response = await client.post(
            f"/entities/{entity_id}/properties/P31",
            json=claim_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 201]


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
        response = await client.post(
            "/entities/items",
            json=sample_item_with_statements,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get property hashes
        response = await client.get(f"/entities/{entity_id}/properties/P31")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "hashes" in data


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
            "/entities/items",
            json=sample_item_with_statements,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get property hashes via alternative endpoint
        response = await client.get(f"{api_prefix}/{entity_id}/properties/P31")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "hashes" in data
