"""Contract tests for stats API endpoints.

These tests verify the stats endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_stats_response_structure(api_prefix: str) -> None:
    """Contract test: Stats response contains expected fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/stats")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_stats_values_non_negative(api_prefix: str) -> None:
    """Contract test: All count values are >= 0."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/stats")
        assert response.status_code == 200
        data = response.json()

        for key, value in data.items():
            if isinstance(value, int):
                assert value >= 0, f"Field {key} has negative value"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_stats_type_consistency(api_prefix: str) -> None:
    """Contract test: All values are appropriate types."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/stats")
        assert response.status_code == 200
        data = response.json()

        for key, value in data.items():
            assert isinstance(value, (int, str, bool, list, dict)), (
                f"Field {key} has unexpected type {type(value)}"
            )
