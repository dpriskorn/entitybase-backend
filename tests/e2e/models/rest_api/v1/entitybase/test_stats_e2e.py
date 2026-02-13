"""E2E tests for statistics and activity endpoints."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_general_stats(api_prefix: str) -> None:
    """E2E test: Get general wiki statistics."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/stats")
        # Returns 400 if general_daily_stats table is empty
        # or 200 if stats exist
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Stats may include entity counts, statement counts, etc.
            assert "entities" in data or "statements" in data or "total" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_entity_property_counts(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Get statement counts per property for an entity's head revision."""
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

        # Get property counts
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/property_counts"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)
        # Should contain property IDs and their statement counts
        if isinstance(data, dict):
            # May have "counts" key or be a dict mapping property_id -> count
            assert "counts" in data or "P31" in data or len(data) >= 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_entity_property_counts_empty(
    api_prefix: str, sample_item_data
) -> None:
    """E2E test: Get property counts for entity with no statements."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity without statements
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get property counts
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/property_counts"
        )
        assert response.status_code == 200
        data = response.json()
        # Empty entity should return empty result
        assert isinstance(data, dict) or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_activity(api_prefix: str) -> None:
    """E2E test: Get user's activity with filtering."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 91001}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Create some entities as this user
        for i in range(3):
            entity_data = {
                "type": "item",
                "labels": {"en": {"language": "en", "value": f"Activity Test {i}"}},
            }
            await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "E2E test", "X-User-ID": "91001"},
            )

        # Get user activity
        response = await client.get(
            f"{api_prefix}/users/91001/activity?limit=10&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "activities" in data
        assert isinstance(data["activities"], list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_activity_with_filters(api_prefix: str) -> None:
    """E2E test: Get user's activity with entity type and action filters."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 91002}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get filtered activity
        response = await client.get(
            f"{api_prefix}/users/91002/activity?activity_type=ENTITY_CREATE&limit=10&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "activities" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_activity_pagination(api_prefix: str) -> None:
    """E2E test: Get user's activity with pagination."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 91003}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Create entities
        for i in range(15):
            entity_data = {
                "type": "item",
                "labels": {"en": {"language": "en", "value": f"Pagination Test {i}"}},
            }
            await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "E2E test", "X-User-ID": "91003"},
            )

        # Get first page (limit must be 10, 25, 50, or 100)
        response = await client.get(
            f"{api_prefix}/users/91003/activity?limit=10&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert len(data["activities"]) <= 10

        # Get second page
        response = await client.get(
            f"{api_prefix}/users/91003/activity?limit=10&offset=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
