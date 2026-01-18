import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")

from datetime import date


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_user_new() -> None:
    """Test creating a new user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/entitybase/v1/users", json={"user_id": 12345})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["created"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_user_existing() -> None:
    """Test creating a user that already exists"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First create
        response1 = await client.post("/entitybase/v1/users", json={"user_id": 12345})
        assert response1.status_code == 200
        assert response1.json()["created"] is True

        # Second create (should return created=False)
        response2 = await client.post("/entitybase/v1/users", json={"user_id": 12345})
        assert response2.status_code == 200
        data = response2.json()
        assert data["user_id"] == 12345
        assert data["created"] is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_existing() -> None:
    """Test getting an existing user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First create user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        # Then get user
        response = await client.get("/entitybase/v1/users/12345")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_not_found() -> None:
    """Test getting a non-existing user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entitybase/v1/users/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_user_invalid() -> None:
    """Test creating a user with invalid data"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Invalid user_id (negative)
        response = await client.post("/entitybase/v1/users", json={"user_id": -1})
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_toggle_watchlist_enable() -> None:
    """Test enabling watchlist for user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        # Toggle to disable first
        await client.put(
            "/entitybase/v1/users/12345/watchlist/toggle", json={"enabled": False}
        )

        # Then enable
        response = await client.put(
            "/entitybase/v1/users/12345/watchlist/toggle", json={"enabled": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["enabled"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_toggle_watchlist_disable() -> None:
    """Test disabling watchlist for user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        # Disable
        response = await client.put(
            "/entitybase/v1/users/12345/watchlist/toggle", json={"enabled": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["enabled"] is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_toggle_watchlist_user_not_registered() -> None:
    """Test toggle for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            "/entitybase/v1/users/99999/watchlist/toggle", json={"enabled": True}
        )
        assert response.status_code == 400
        assert "User not registered" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_activity() -> None:
    """Test getting user activity"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        # Get activity (should be empty initially)
        response = await client.get("/entitybase/v1/users/12345/activity")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["activities"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_activity_user_not_registered() -> None:
    """Test getting activity for unregistered user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entitybase/v1/users/99999/activity")
        assert response.status_code == 400
        assert "User not registered" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_activity_invalid_type() -> None:
    """Test getting activity with invalid type filter"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        response = await client.get("/entitybase/v1/users/12345/activity?type=invalid")
        assert response.status_code == 400
        assert "Invalid activity type" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_activity_invalid_limit() -> None:
    """Test getting activity with invalid limit"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        response = await client.get("/entitybase/v1/users/12345/activity?limit=1000")
        assert response.status_code == 400
        assert "Limit must be one of" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_stats() -> None:
    """Test getting user statistics"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entitybase/v1/users/stat")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "date" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["active_users"], int)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_general_stats() -> None:
    """Test getting general wiki statistics"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/entitybase/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_statements" in data
        assert "total_qualifiers" in data
        assert "total_references" in data
        assert "total_items" in data
        assert "total_lexemes" in data
        assert "total_properties" in data
        assert "total_sitelinks" in data
        assert "total_terms" in data
        assert "terms_per_language" in data
        assert "terms_by_type" in data
        assert "date" in data
        assert isinstance(data["total_statements"], int)
        assert isinstance(data["terms_per_language"], dict)
        assert isinstance(data["terms_by_type"], dict)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_watchlist_add() -> None:
    """Test adding a watchlist entry"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})
        # Enable watchlist
        await client.put(
            "/entitybase/v1/users/12345/watchlist/toggle", json={"enabled": True}
        )

        response = await client.post(
            "/entitybase/users/12345/watchlist",
            json={"entity_id": "Q42", "properties": ["P31"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Watch added"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_watchlist_get() -> None:
    """Test getting user's watchlist"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})
        # Enable watchlist
        await client.put(
            "/entitybase/v1/users/12345/watchlist/toggle", json={"enabled": True}
        )

        response = await client.get("/entitybase/users/12345/watchlist")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert "watches" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_watchlist_notifications() -> None:
    """Test getting watchlist notifications"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})
        # Enable watchlist
        await client.put(
            "/entitybase/v1/users/12345/watchlist/toggle", json={"enabled": True}
        )

        response = await client.get("/entitybase/users/12345/watchlist/notifications")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert "notifications" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_watchlist_stats() -> None:
    """Test getting watchlist statistics"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post("/entitybase/v1/users", json={"user_id": 12345})

        response = await client.get("/entitybase/users/12345/watchlist/stats")
        assert response.status_code == 200
        data = response.json()
        assert "entity_count" in data
        assert "property_count" in data
