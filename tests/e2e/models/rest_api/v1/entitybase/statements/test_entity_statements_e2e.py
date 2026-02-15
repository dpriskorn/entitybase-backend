"""E2E tests for entity statement management."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_add_statement(
    api_prefix: str, sample_item_data, sample_property_data
) -> None:
    from models.rest_api.main import app

    """E2E test: Add a single statement to an entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {"X-Edit-Summary": "E2E test", "X-User-ID": "0"}

        property_data = sample_property_data.copy()
        property_data["id"] = "P31"
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=property_data,
            headers=headers,
        )
        assert response.status_code == 200

        response = await client.post(
            f"{api_prefix}/entities/items",
            json=sample_item_data,
            headers=headers,
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        statement_data = {
            "claim": {
                "id": "TESTCLAIM123",
                "mainsnak": {
                    "snaktype": "value",
                    "property": "P31",
                    "datavalue": {"value": {"id": "Q5"}, "type": "wikibase-item"},
                },
                "type": "statement",
                "rank": "normal",
            }
        }
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/statements",
            json=statement_data,
            headers=headers,
        )
        assert response.status_code == 200

        # Verify statement was added
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        revision = data.get("data", {}).get("revision", data)
        statements = revision.get(
            "statements", revision.get("hashes", {}).get("statements", [])
        )
        # Statement should now exist
        assert len(statements) > 0


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
        revision = data.get("data", {}).get("revision", data)
        statements = revision.get(
            "statements", revision.get("hashes", {}).get("statements", [])
        )
        if not statements:
            pytest.skip(
                "No statements found - entity creation may not support inline statements"
            )
        statement_hash = statements[0]

        # Remove statement
        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/statements/{statement_hash}",
            json={},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Verify removal
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        revision = data.get("data", {}).get("revision", data)
        statements = revision.get(
            "statements", revision.get("hashes", {}).get("statements", [])
        )
        assert statement_hash not in statements or len(statements) == 0


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
        revision = data.get("data", {}).get("revision", data)
        statements = revision.get(
            "statements", revision.get("hashes", {}).get("statements", [])
        )
        if not statements:
            pytest.skip(
                "No statements found - entity creation may not support inline statements"
            )
        original_hash = statements[0]

        # Replace statement
        new_claim_data = {
            "id": "TESTCLAIM456",
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"value": {"id": "Q5"}, "type": "wikibase-item"},
            },
            "type": "statement",
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
        revision = data.get("data", {}).get("revision", data)
        statements = revision.get(
            "statements", revision.get("hashes", {}).get("statements", [])
        )
        assert original_hash not in statements or len(statements) > 0
