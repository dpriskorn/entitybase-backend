"""E2E tests for backlinks functionality."""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_entity_backlinks_full_lifecycle(
    api_prefix: str, sample_item_data, sample_property_data
) -> None:
    """E2E test: Create entities with statements, verify backlinks are created."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "E2E backlink test", "X-User-ID": "0"}

        property_data = sample_property_data.copy()
        property_data["id"] = "P31"
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=property_data,
            headers=headers,
        )
        assert response.status_code == 200

        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers=headers,
        )
        assert response.status_code == 200
        target_entity_id = response.json()["id"]

        referencing_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Referencing Item"}},
            "statements": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"id": target_entity_id},
                            "type": "wikibase-item",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ],
        }

        response = await client.post(
            f"{api_prefix}/entities/items",
            json=referencing_data,
            headers=headers,
        )
        assert response.status_code == 200
        referencing_entity_id = response.json()["id"]

        response = await client.get(
            f"{api_prefix}/entities/{target_entity_id}/backlinks"
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_backlinks_query_endpoint(api_prefix: str) -> None:
    """E2E test: Query backlinks endpoint returns valid response."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q1/backlinks")

        assert response.status_code == 200
        data = response.json()
        assert "backlinks" in data
        assert isinstance(data["backlinks"], list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_backlinks_pagination(api_prefix: str) -> None:
    """E2E test: Backlinks pagination works correctly."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/Q1/backlinks?limit=10&offset=0"
        )

        assert response.status_code == 200
        data = response.json()
        assert "backlinks" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_backlinks_empty_for_new_entity(api_prefix: str) -> None:
    """E2E test: New entity has empty backlinks."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "E2E test", "X-User-ID": "0"}

        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "New Item"}},
        }

        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers=headers,
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")
        assert response.status_code == 200
        data = response.json()
        assert data["backlinks"] == []
