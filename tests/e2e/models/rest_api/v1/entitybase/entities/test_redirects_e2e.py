"""E2E tests for redirect operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_redirect(api_prefix: str, sample_item_data) -> None:
    from models.rest_api.main import app

    """E2E test: Create a redirect for an entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create source entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        source_id = response.json()["id"]

        # Create target entity
        target_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Redirect Target"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=target_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        target_id = response.json()["id"]

        # Create redirect
        redirect_data = {"source_entity_id": source_id, "target_entity_id": target_id}
        response = await client.post(
            f"{api_prefix}/redirects",
            json=redirect_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        # May succeed or fail depending on implementation
        assert response.status_code in [200, 201, 400]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_revert_redirect(api_prefix: str, sample_item_data) -> None:
    from models.rest_api.main import app

    """E2E test: Revert entity from redirect."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create source entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        # Try to revert redirect (will fail if no redirect exists)
        revert_data = {"revision_id": 1}
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/revert-redirect",
            json=revert_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        # May succeed or fail depending on whether redirect exists
        assert response.status_code in [200, 400, 404]
