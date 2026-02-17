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
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Label"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

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
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "descriptions": {"en": {"language": "en", "value": "Test Description"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

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
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "aliases": {
                    "en": [
                        {"language": "en", "value": "Alias1"},
                        {"language": "en", "value": "Alias2"},
                    ]
                },
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        aliases_resp = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert aliases_resp.status_code == 200
        data = aliases_resp.json()

        assert "aliases" in data
        assert isinstance(data["aliases"], list)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_label_language_field(api_prefix: str) -> None:
    """Contract test: Label includes language code."""
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

        get_resp = await client.get(f"{api_prefix}/entities/{create_resp.json()['id']}")
        assert get_resp.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_label_not_found(api_prefix: str) -> None:
    """Contract test: Non-existent label returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={"type": "item"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        label_resp = await client.get(f"{api_prefix}/entities/{entity_id}/labels/xx")
        assert label_resp.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_description_not_found(api_prefix: str) -> None:
    """Contract test: Non-existent description returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={"type": "item"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        desc_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/xx"
        )
        assert desc_resp.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_aliases_not_found(api_prefix: str) -> None:
    """Contract test: Non-existent aliases returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={"type": "item"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        aliases_resp = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/xx")
        assert aliases_resp.status_code == 404
