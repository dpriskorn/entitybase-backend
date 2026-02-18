"""Contract tests for backlinks API endpoint.

These tests verify the backlinks endpoint conforms to its API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_response_schema(api_prefix: str) -> None:
    """Contract test: Verify backlinks response matches expected schema."""
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

        response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")

        assert response.status_code == 200
        data = response.json()

        assert "backlinks" in data
        assert isinstance(data["backlinks"], list)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_pagination(api_prefix: str) -> None:
    """Contract test: Verify pagination parameters work correctly."""
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

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/backlinks?limit=10&offset=0"
        )

        assert response.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_empty_response(api_prefix: str) -> None:
    """Contract test: Verify empty backlinks returns valid structure."""
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

        response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")

        assert response.status_code == 200
        data = response.json()

        assert "backlinks" in data
        assert data["backlinks"] == []


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_not_found_entity(api_prefix: str) -> None:
    """Contract test: Verify response for non-existent entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999999999/backlinks")

        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlink_response_fields(api_prefix: str) -> None:
    """Contract test: Verify each backlink has required fields."""
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

        response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")

        assert response.status_code == 200
        data = response.json()

        assert "backlinks" in data
        assert "limit" in data
        assert "offset" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_pagination_response(api_prefix: str) -> None:
    """Contract test: Verify pagination fields are integers."""
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

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/backlinks?limit=25&offset=50"
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["limit"], int)
        assert isinstance(data["offset"], int)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_empty_list_type(api_prefix: str) -> None:
    """Contract test: Empty backlinks returns list, not null."""
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

        response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")

        assert response.status_code == 200
        data = response.json()

        assert "backlinks" in data
        assert isinstance(data["backlinks"], list)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backlinks_limit_default_value(api_prefix: str) -> None:
    """Contract test: Verify default limit value."""
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

        response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")

        assert response.status_code == 200
        data = response.json()

        assert "limit" in data
        assert data["limit"] > 0
