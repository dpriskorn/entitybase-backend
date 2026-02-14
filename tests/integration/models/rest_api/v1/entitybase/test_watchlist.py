import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_watch(api_prefix: str, initialized_app: None) -> None:
    """Test adding a watch"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "test", "X-User-ID": "0"}

        # Create Q42 entity first
        Q42_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {
                "en": {"language": "en", "value": "British science fiction writer"}
            },
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=Q42_data,
            headers=headers,
        )
        assert response.status_code == 200

        # Register user
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        # Add watch
        response = await client.post(
            f"{api_prefix}/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch added"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_watch_user_not_registered(
    api_prefix: str, initialized_app: None
) -> None:
    """Test adding a watch for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/users/99999/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        assert "User not registered" in response.json()["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_watch(api_prefix: str, initialized_app: None) -> None:
    """Test removing a watch"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "test", "X-User-ID": "0"}

        # Create Q42 entity first
        Q42_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {
                "en": {"language": "en", "value": "British science fiction writer"}
            },
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=Q42_data,
            headers=headers,
        )
        assert response.status_code == 200

        # Register user and add watch
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        await client.post(
            f"{api_prefix}/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        # Remove watch
        response = await client.post(
            f"{api_prefix}/users/12345/watchlist/remove",
            json={"entity_id": "Q42", "properties": ["P31"]},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch removed"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_watchlist(api_prefix: str, initialized_app: None) -> None:
    """Test getting user's watchlist"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "test", "X-User-ID": "0"}

        # Create Q42 entity first
        Q42_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {
                "en": {"language": "en", "value": "British science fiction writer"}
            },
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=Q42_data,
            headers=headers,
        )
        assert response.status_code == 200

        # Register user and add watch
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        await client.post(
            f"{api_prefix}/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        # Get watchlist
        response = await client.get(f"{api_prefix}/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert len(data["watches"]) == 1
        assert data["watches"][0]["entity_id"] == "Q42"
        assert data["watches"][0]["properties"] == ["P31"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_watchlist_user_not_registered(
    api_prefix: str, initialized_app: None
) -> None:
    """Test getting watchlist for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/users/99999/watchlist")
        assert response.status_code == 400
        assert "User not registered" in response.json()["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_watch_by_id(api_prefix: str, initialized_app: None) -> None:
    """Test removing a watch by ID"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "test", "X-User-ID": "0"}

        # Create Q42 entity first
        Q42_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {
                "en": {"language": "en", "value": "British science fiction writer"}
            },
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=Q42_data,
            headers=headers,
        )
        assert response.status_code == 200

        # Register user and add watch
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        await client.post(
            f"{api_prefix}/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        # Get watchlist to obtain the watch ID
        response = await client.get(f"{api_prefix}/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        watch_id = data["watches"][0]["id"]

        # Remove watch by ID
        response = await client.delete(
            f"{api_prefix}/users/12345/watchlist/{watch_id}",
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch removed"

        # Verify watch is removed
        response = await client.get(f"{api_prefix}/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        assert len(data["watches"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_notifications(api_prefix: str, initialized_app: None) -> None:
    """Test getting user notifications"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        # Get notifications (should be empty initially)
        response = await client.get(f"{api_prefix}/users/12345/watchlist/notifications")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["notifications"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_notifications_user_not_registered(
    api_prefix: str, initialized_app: None
) -> None:
    """Test getting notifications for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/users/99999/watchlist/notifications")
        assert response.status_code == 404
        assert "User not registered" in response.json()["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mark_notification_checked(
    api_prefix: str, initialized_app: None
) -> None:
    """Test marking notification as checked"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        # Mark notification checked (even if doesn't exist, should not error)
        response = await client.put(
            f"{api_prefix}/users/12345/watchlist/notifications/1/check",
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Notification marked as checked"
