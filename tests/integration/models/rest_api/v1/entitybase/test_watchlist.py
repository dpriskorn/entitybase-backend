import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_watch() -> None:
    """Test adding a watch"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First register user
        await client.post("/v1/entitybase/users", json={"user_id": 12345})

        # Add watch
        response = await client.post(
            "/v1/entitybase/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch added"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_watch_user_not_registered() -> None:
    """Test adding a watch for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/users/12345/watchlist",
            json={"user_id": 99999, "entity_id": "Q42", "properties": ["P31"]},
        )
        assert response.status_code == 400
        assert "User not registered" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_watch() -> None:
    """Test removing a watch"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user and add watch
        await client.post("/v1/entitybase/users", json={"user_id": 12345})
        await client.post(
            "/v1/entitybase/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
        )

        # Remove watch
        response = await client.request(
            "DELETE",
            "/v1/entitybase/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch removed"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_watchlist() -> None:
    """Test getting user's watchlist"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user and add watch
        await client.post("/v1/entitybase/users", json={"user_id": 12345})
        await client.post(
            "/v1/entitybase/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
        )

        # Get watchlist
        response = await client.get("/v1/entitybase/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert len(data["watches"]) == 1
        assert data["watches"][0]["entity_id"] == "Q42"
        assert data["watches"][0]["properties"] == ["P31"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_watchlist_user_not_registered() -> None:
    """Test getting watchlist for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/v1/entitybase/users/99999/watchlist")
        assert response.status_code == 400
        assert "User not registered" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_watch_by_id() -> None:
    """Test removing a watch by ID"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user and add watch
        await client.post("/v1/entitybase/users", json={"user_id": 12345})
        await client.post(
            "/v1/entitybase/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
        )

        # Get watchlist to obtain the watch ID
        response = await client.get("/v1/entitybase/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        watch_id = data["watches"][0]["id"]

        # Remove watch by ID
        response = await client.delete(
            f"/v1/entitybase/users/12345/watchlist/{watch_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch removed"

        # Verify watch is removed
        response = await client.get("/v1/entitybase/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        assert len(data["watches"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_notifications() -> None:
    """Test getting user notifications"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/v1/entitybase/users", json={"user_id": 12345})

        # Get notifications (should be empty initially)
        response = await client.get(
            "/v1/entitybase/users/12345/watchlist/notifications"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["notifications"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_notifications_user_not_registered() -> None:
    """Test getting notifications for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/v1/entitybase/users/99999/watchlist/notifications"
        )
        assert response.status_code == 400
        assert "User not registered" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mark_notification_checked() -> None:
    """Test marking notification as checked"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/v1/entitybase/users", json={"user_id": 12345})

        # Mark notification checked (even if doesn't exist, should not error)
        response = await client.post(
            "/v1/entitybase/users/12345/watchlist/notifications/check",
            json={"notification_id": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Notification marked as checked"
