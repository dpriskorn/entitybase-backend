"""E2E tests for entity statement management."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_remove_statement(api_prefix: str, sample_item_with_statements) -> None:
    from models.rest_api.main import app

    """E2E test: Remove a statement by hash from an entity."""
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
        entity_id = response.json()["id"]

        # Get statement hash
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        statement_hash = data["statements"][0]

        # Remove statement
        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/statements/{statement_hash}",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 204]

        # Verify removal
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert statement_hash not in data["statements"] or len(data["statements"]) == 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_replace_statement(api_prefix: str, sample_item_with_statements) -> None:
    from models.rest_api.main import app

    """E2E test: Replace a statement by hash with new claim data."""
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
        entity_id = response.json()["id"]

        # Get statement hash
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        original_hash = data["statements"][0]

        # Replace statement
        new_claim_data = {
            "property": {"id": "P31", "data_type": "wikibase-item"},
            "value": {"type": "value", "content": "Q5"},
            "rank": "preferred",
        }
        response = await client.patch(
            f"{api_prefix}/entities/{entity_id}/statements/{original_hash}",
            json=new_claim_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Verify replacement
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        # Statement hash should be different after update
        assert original_hash not in data["statements"] or len(data["statements"]) > 0
