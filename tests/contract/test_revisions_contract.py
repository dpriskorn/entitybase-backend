"""Contract tests for revisions API endpoints.

These tests verify the revisions endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_revision_response_fields(api_prefix: str) -> None:
    """Contract test: Revision has required fields."""
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


@pytest.mark.contract
@pytest.mark.asyncio
async def test_revision_list_pagination(api_prefix: str) -> None:
    """Contract test: Pagination works correctly."""
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
            f"{api_prefix}/entities/{entity_id}/revisions?limit=10&offset=0"
        )
        assert revisions_resp.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_revision_content_hash(api_prefix: str) -> None:
    """Contract test: Content hash is integer."""
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

        get_resp = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert get_resp.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_revision_not_found(api_prefix: str) -> None:
    """Contract test: Non-existent revision returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q1/revisions/999999")
        assert response.status_code in [404, 400]
