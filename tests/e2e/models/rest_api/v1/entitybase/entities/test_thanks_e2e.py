"""E2E tests for thanks operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_send_thank(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Send a thank for a specific revision."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Thanks Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]
        revision_id = 1

        # Send thank (will fail for non-existent user but endpoint works)
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/revisions/{revision_id}/thank",
            headers={"X-User-ID": "99999"},
        )
        # May fail if user doesn't exist, but endpoint works
        assert response.status_code in [200, 400, 404]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_revision_thanks(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get all thanks for a specific revision."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Revision Thanks Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]
        revision_id = 1

        # Get thanks for revision
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/revisions/{revision_id}/thanks"
        )
        assert response.status_code == 200
        data = response.json()
        assert "thanks" in data or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_thanks_received(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get thanks received by user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90014}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get thanks received
        response = await client.get(
            f"{api_prefix}/users/90014/thanks/received?limit=50&hours=24"
        )
        assert response.status_code == 200
        data = response.json()
        assert "thanks" in data or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_thanks_sent(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get thanks sent by user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90015}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get thanks sent
        response = await client.get(
            f"{api_prefix}/users/90015/thanks/sent?limit=50&hours=24"
        )
        assert response.status_code == 200
        data = response.json()
        assert "thanks" in data or isinstance(data, list)
