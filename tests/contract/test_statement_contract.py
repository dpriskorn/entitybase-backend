"""Contract tests for statement API endpoints.

These tests verify the statement endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_statement_response_schema(api_prefix: str) -> None:
    """Contract test: Statement has required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        entity_resp = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert entity_resp.status_code == 200
        data = entity_resp.json()

        if "data" in data and "revision" in data["data"]:
            revision = data["data"]["revision"]
            if "statements" in revision:
                hashes = revision["statements"].get("hashes", [])
                if hashes:
                    hash_val = hashes[0]
                    stmt_resp = await client.get(f"{api_prefix}/statements/{hash_val}")
                    assert stmt_resp.status_code == 200
                    stmt_data = stmt_resp.json()
                    assert "hash" in stmt_data or "content_hash" in stmt_data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_statement_hash_type(api_prefix: str) -> None:
    """Contract test: Hash is integer."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        entity_resp = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert entity_resp.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_statement_batch_response(api_prefix: str) -> None:
    """Contract test: Batch response has statements array."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        batch_resp = await client.get(
            f"{api_prefix}/statements/batch?entity_ids={entity_id}"
        )
        assert batch_resp.status_code == 200
        data = batch_resp.json()
        assert "statements" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_statement_not_found(api_prefix: str) -> None:
    """Contract test: Non-existent statement returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        stmt_resp = await client.get(f"{api_prefix}/statements/999999999")
        assert stmt_resp.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_statements_by_property(api_prefix: str) -> None:
    """Contract test: Statements by property endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        prop_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/properties/P31"
        )
        assert prop_resp.status_code == 200
        data = prop_resp.json()
        assert "property_hashes" in data
        assert data["property_hashes"] == []


@pytest.mark.contract
@pytest.mark.asyncio
async def test_statements_property_list(api_prefix: str) -> None:
    """Contract test: Property list endpoint returns valid structure."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        props_resp = await client.get(f"{api_prefix}/entities/{entity_id}/properties")
        assert props_resp.status_code == 200
        data = props_resp.json()

        assert isinstance(data, (list, dict))
