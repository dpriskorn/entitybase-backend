"""E2E tests for hash-based operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_batch_statements(
    api_prefix: str, sample_item_with_statements
) -> None:
    """E2E test: Retrieve multiple statements by their content hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_with_statements,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()

        # Get statement hashes
        entity_id = data["id"]
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        entity_data = response.json()

        # Get batch statements
        statement_hashes = entity_data.get("statements", [])
        if statement_hashes:
            batch_request = {
                "content_hashes": statement_hashes[:1]  # Get first statement
            }
            response = await client.post(
                f"{api_prefix}/entitybase/v1/statements/batch", json=batch_request
            )
            assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_fetch_qualifiers(api_prefix: str) -> None:
    """E2E test: Fetch qualifiers by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Fetch qualifiers (may return empty if no hashes exist)
        response = await client.get(f"{api_prefix}/qualifiers/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_fetch_references(api_prefix: str) -> None:
    """E2E test: Fetch references by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Fetch references (may return empty if no hashes exist)
        response = await client.get(f"{api_prefix}/references/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_fetch_snaks(api_prefix: str) -> None:
    """E2E test: Fetch snaks by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Fetch snaks (may return empty if no hashes exist)
        response = await client.get(f"{api_prefix}/snaks/123,456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
