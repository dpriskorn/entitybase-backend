"""Contract tests for terms API endpoints (labels, descriptions, aliases).

These tests verify the terms endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_label_response_schema(api_prefix: str) -> None:
    """Contract test: Label response has required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["data"]["entity_id"]

        await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Test Label"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        label_resp = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
        assert label_resp.status_code == 200
        data = label_resp.json()

        assert "value" in data
        assert isinstance(data["value"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_description_response_schema(api_prefix: str) -> None:
    """Contract test: Description response has required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["data"]["entity_id"]

        await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Test Description"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        desc_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/en"
        )
        assert desc_resp.status_code == 200
        data = desc_resp.json()

        assert "value" in data
        assert isinstance(data["value"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_aliases_response_schema(api_prefix: str) -> None:
    """Contract test: Aliases returns list of strings."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["data"]["entity_id"]

        await client.put(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=[{"value": "Test Alias"}],
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        aliases_resp = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert aliases_resp.status_code == 200
        data = aliases_resp.json()

        assert isinstance(data, list)
        assert len(data) > 0
