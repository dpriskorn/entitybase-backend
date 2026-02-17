"""Contract tests for entity API endpoints.

These tests verify the entity endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_response_required_fields(api_prefix: str) -> None:
    """Contract test: Entity response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        get_resp = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()

        assert "id" in data
        assert "data" in data
        assert "revision" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_data_structure(api_prefix: str) -> None:
    """Contract test: Entity data contains expected nested structure."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        get_resp = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()

        assert "id" in data["data"]
        assert "revision" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_type_field(api_prefix: str) -> None:
    """Contract test: Entity type matches expected value."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Item"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200

        get_resp = await client.get(f"{api_prefix}/entities/{create_resp.json()['id']}")
        assert get_resp.status_code == 200
        data = get_resp.json()

        assert "revision" in data
        assert "entity_type" in data["revision"] or "type" in data["revision"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_id_format(api_prefix: str) -> None:
    """Contract test: Entity ID follows expected format (Q#, P#, L#)."""
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

        assert (
            entity_id.startswith("Q")
            or entity_id.startswith("P")
            or entity_id.startswith("L")
        )


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_revision_is_integer(api_prefix: str) -> None:
    """Contract test: Revision ID is an integer."""
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
        data = get_resp.json()

        assert isinstance(data["revision"], int)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_revisions_list(api_prefix: str) -> None:
    """Contract test: Revisions list endpoint returns valid structure."""
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

        revisions_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/revisions"
        )
        assert revisions_resp.status_code == 200
        data = revisions_resp.json()

        assert isinstance(data, (list, dict))


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_not_found(api_prefix: str) -> None:
    """Contract test: Non-existent entity returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999999999")
        assert response.status_code == 404
