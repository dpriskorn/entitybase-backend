"""E2E tests for batch entity data operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_batch_aliases(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get batch aliases by hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Get batch aliases (may return empty if no hashes exist yet)
        response = await client.get(f"{api_prefix}/entities/aliases/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_batch_descriptions(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get batch descriptions by hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Get batch descriptions (may return empty if no hashes exist yet)
        response = await client.get(f"{api_prefix}/entities/descriptions/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_batch_labels(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get batch labels by hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Get batch labels (may return empty if no hashes exist yet)
        response = await client.get(f"{api_prefix}/entities/labels/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_batch_sitelinks(api_prefix: str, sample_item_data) -> None:
    """E2E test: Get batch sitelink titles by hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"/entities/items",
            json=sample_item_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Get batch sitelinks (may return empty if no hashes exist yet)
        response = await client.get(f"{api_prefix}/entities/sitelinks/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
