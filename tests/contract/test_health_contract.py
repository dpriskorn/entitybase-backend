"""Contract tests for health API endpoint.

These tests verify the health endpoint conforms to its API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_health_response_schema(api_prefix: str) -> None:
    """Contract test: Health has status field."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert isinstance(data["status"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_health_status_values(api_prefix: str) -> None:
    """Contract test: Status is expected value."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["ok", "error", "healthy", "unhealthy"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_health_optional_details(api_prefix: str) -> None:
    """Contract test: Details field structure when present."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()

        if "details" in data:
            assert isinstance(data["details"], dict)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_health_response_type(api_prefix: str) -> None:
    """Contract test: Health response is a dict."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
