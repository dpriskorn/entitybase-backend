"""Contract tests for authentication API endpoints.

These tests verify the auth endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_login_response_schema(api_prefix: str) -> None:
    """Contract test: Login response structure for invalid credentials."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/auth/login",
            json={"username": "nonexistent", "password": "wrong"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_login_validation_error(api_prefix: str) -> None:
    """Contract test: Login returns 422 for invalid input."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/auth/login",
            json={"username": "", "password": ""},
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_register_requires_auth(api_prefix: str) -> None:
    """Contract test: Register returns 401 without auth."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http/test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/auth/register",
            json={"username": "newuser", "password": "password123"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_register_validation_error(
    api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Contract test: Register returns 422 for invalid input."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/auth/register",
            json={"username": "ab", "password": "short"},
            headers={"X-Edit-Summary": "test", **auth_headers},
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_user_requires_auth(api_prefix: str) -> None:
    """Contract test: Delete user returns 401 without auth."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"{api_prefix}/auth/users/1",
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_nonexistent_user(
    api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Contract test: Delete non-existent user returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"{api_prefix}/auth/users/99999",
            headers={"X-Edit-Summary": "test", **auth_headers},
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_login_missing_edit_summary(api_prefix: str) -> None:
    """Contract test: Login doesn't require X-Edit-Summary (no auth dep)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http/test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/auth/login",
            json={"username": "test", "password": "pass"},
        )
        assert response.status_code == 401
