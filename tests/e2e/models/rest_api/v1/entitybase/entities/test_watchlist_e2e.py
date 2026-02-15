"""E2E tests for watchlist operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_add_watch(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Add a watchlist entry for user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90006}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Create entity
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Watch Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        # Add watch
        watch_data = {"entity_id": entity_id, "properties": ["P31"]}
        response = await client.post(
            f"{api_prefix}/users/90006/watchlist", json=watch_data
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_watchlist(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get user's watchlist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90007}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Create entity
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Watchlist Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        # Add watch
        watch_data = {"entity_id": entity_id, "properties": ["P31"]}
        await client.post(f"{api_prefix}/users/90007/watchlist", json=watch_data)

        # Get watchlist
        response = await client.get(f"{api_prefix}/users/90007/watchlist")
        assert response.status_code == 200
        data = response.json()
        assert "watches" in data
        assert len(data["watches"]) > 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_remove_watch_by_id(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Remove a watchlist entry by ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90008}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Create entity
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Watch Remove Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        # Add watch
        watch_data = {"entity_id": entity_id, "properties": ["P31"]}
        await client.post(f"{api_prefix}/users/90008/watchlist", json=watch_data)

        # Get watchlist to get watch ID
        response = await client.get(f"{api_prefix}/users/90008/watchlist")
        watch_id = response.json()["watches"][0]["id"]

        # Remove by ID
        response = await client.delete(f"{api_prefix}/users/90008/watchlist/{watch_id}")
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_toggle_watchlist(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Enable or disable watchlist for user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90009}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Toggle watchlist
        toggle_data = {"enabled": True}
        response = await client.put(
            f"{api_prefix}/users/90009/watchlist/toggle", json=toggle_data
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_remove_watch_by_entity(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Remove a watchlist entry by entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90010}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Create entity
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Watch Remove Entity Test"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        # Add watch
        watch_data = {"entity_id": entity_id, "properties": ["P31"]}
        await client.post(f"{api_prefix}/users/90010/watchlist", json=watch_data)

        # Remove by entity
        response = await client.post(
            f"{api_prefix}/users/90010/watchlist/remove", json={"entity_id": entity_id}
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_watchlist_stats(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get user's watchlist statistics."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90011}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get watchlist stats
        response = await client.get(f"{api_prefix}/users/90011/watchlist/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_watches" in data or "count" in data or "entity_count" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_watchlist_notifications(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get user's recent watchlist notifications."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90012}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get notifications
        response = await client.get(
            f"{api_prefix}/users/90012/watchlist/notifications?hours=24&limit=50&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "notifications" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_mark_notification_checked(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Mark a notification as checked."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        user_data = {"user_id": 90013}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Mark notification as checked
        response = await client.put(
            f"{api_prefix}/users/90013/watchlist/notifications/123/check"
        )
        # Returns 200 (idempotent operation - succeeds even if notification doesn't exist)
        assert response.status_code == 200
