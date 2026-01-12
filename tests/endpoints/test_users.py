import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
async def test_create_user_new() -> None:
    """Test creating a new user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/v1/users", json={"user_id": 12345})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert data["created"] is True


@pytest.mark.asyncio
async def test_create_user_existing() -> None:
    """Test creating a user that already exists"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First create
        response1 = await client.post("/v1/users", json={"user_id": 12345})
        assert response1.status_code == 200
        assert response1.json()["created"] is True

        # Second create (should return created=False)
        response2 = await client.post("/v1/users", json={"user_id": 12345})
        assert response2.status_code == 200
        data = response2.json()
        assert data["user_id"] == 12345
        assert data["created"] is False


@pytest.mark.asyncio
async def test_get_user_existing() -> None:
    """Test getting an existing user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First create user
        await client.post("/v1/users", json={"user_id": 12345})

        # Then get user
        response = await client.get("/v1/users/12345")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 12345
        assert "created_at" in data


@pytest.mark.asyncio
async def test_get_user_not_found() -> None:
    """Test getting a non-existing user"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/v1/users/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_invalid() -> None:
    """Test creating a user with invalid data"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Invalid user_id (negative)
        response = await client.post("/v1/users", json={"user_id": -1})
        assert response.status_code == 422  # Validation error
