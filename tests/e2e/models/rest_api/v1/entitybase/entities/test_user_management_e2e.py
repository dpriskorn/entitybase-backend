"""E2E tests for user management operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_user(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Create a new user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        user_data = {"user_id": 90001}
        response = await client.post(f"{api_prefix}/users", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 90001


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_stats(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get user statistics."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user first
        user_data = {"user_id": 90002}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get stats
        response = await client.get(f"{api_prefix}/users/stat")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data or "count" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_info(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get user information by MediaWiki user ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user first
        user_data = {"user_id": 90003}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get user info
        response = await client.get(f"{api_prefix}/users/90003")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 90003


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_endorsements(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get endorsements given by a user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user first
        user_data = {"user_id": 90004}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get user endorsements
        response = await client.get(
            f"{api_prefix}/users/90004/endorsements?limit=10&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert "endorsements" in data
        assert "total_count" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_user_endorsement_stats(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get endorsement statistics for a user."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user first
        user_data = {"user_id": 90005}
        await client.post(f"{api_prefix}/users", json=user_data)

        # Get user endorsement stats
        response = await client.get(f"{api_prefix}/users/90005/endorsements/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 90005
        assert "total_endorsements_given" in data
        assert "total_endorsements_active" in data
