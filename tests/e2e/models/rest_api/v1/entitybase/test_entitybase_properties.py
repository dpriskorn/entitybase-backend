"""E2E tests for property hashes endpoint."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_entity_property_hashes(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Get statement hashes for specified properties in an entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_with_statements,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get property hashes for P31
        response = await client.get(f"{api_prefix}/entity/{entity_id}/properties/P31")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain property hashes


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_entity_property_hashes_multiple_properties(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Get statement hashes for multiple properties."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_with_statements,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get property hashes for multiple properties
        response = await client.get(
            f"{api_prefix}/entity/{entity_id}/properties/P31,P279"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_entity_property_hashes_nonexistent_entity(api_prefix: str) -> None:
    """E2E test: Get property hashes for non-existent entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entity/Q99999999/properties/P31")
        # Should return 404 or empty result
        assert response.status_code in [200, 404]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_entity_property_hashes_empty_entity(api_prefix: str) -> None:
    """E2E test: Get property hashes for entity with no statements."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity without statements
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get property hashes
        response = await client.get(f"{api_prefix}/entity/{entity_id}/properties/P31")
        assert response.status_code == 200
        data = response.json()
        # Empty entity should return empty or minimal result
        assert isinstance(data, dict)
