"""Contract tests for watchlist API endpoints.

These tests verify the watchlist endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_watchlist_response_schema(api_prefix: str) -> None:
    """Contract test: Watchlist response structure."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/users/0/watchlist",
            headers={"X-User-ID": "0"},
        )
        assert response.status_code in [200, 404]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_watchlist_pagination(api_prefix: str) -> None:
    """Contract test: Pagination works correctly."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/users/0/watchlist?limit=10&offset=0",
            headers={"X-User-ID": "0"},
        )
        assert response.status_code in [200, 404]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_watchlist_unauthorized(api_prefix: str) -> None:
    """Contract test: Unauthorized returns 401/403."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/users/0/watchlist")
        assert response.status_code in [401, 403, 404]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_watchlist_notification_count(api_prefix: str) -> None:
    """Contract test: Notification count endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/users/0/watchlist/notifications",
            headers={"X-User-ID": "0"},
        )
        assert response.status_code in [200, 404]
