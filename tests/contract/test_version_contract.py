"""Contract tests for version API endpoint.

These tests verify the version endpoint conforms to its API contract.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.contract
@pytest.mark.asyncio
async def test_version_response_schema() -> None:
    """Contract test: Version has api_version and entitybase_version fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()

        assert "api_version" in data
        assert "entitybase_version" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_version_field_types() -> None:
    """Contract test: Version fields are strings."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["api_version"], str)
        assert isinstance(data["entitybase_version"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_version_fields_non_empty() -> None:
    """Contract test: Version strings are non-empty."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()

        assert len(data["api_version"]) > 0
        assert len(data["entitybase_version"]) > 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_version_response_type() -> None:
    """Contract test: Version response is a dict."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
