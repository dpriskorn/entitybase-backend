"""Contract tests for sitelinks API endpoints.

These tests verify the sitelinks endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_sitelinks_response_schema(api_prefix: str) -> None:
    """Contract test: Sitelinks response structure."""
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

        sitelinks_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/sitelinks"
        )
        assert sitelinks_resp.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_sitelink_fields(api_prefix: str) -> None:
    """Contract test: Sitelink fields structure."""
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

        sitelinks_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/sitelinks"
        )
        assert sitelinks_resp.status_code == 200
        data = sitelinks_resp.json()

        assert isinstance(data, dict)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_sitelinks_empty_structure(api_prefix: str) -> None:
    """Contract test: Empty sitelinks returns dict not null."""
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

        sitelinks_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/sitelinks"
        )
        assert sitelinks_resp.status_code == 200
        data = sitelinks_resp.json()

        assert data is not None
        assert isinstance(data, dict)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_sitelinks_by_site(api_prefix: str) -> None:
    """Contract test: Get sitelink for specific site."""
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

        site_resp = await client.get(
            f"{api_prefix}/entities/{entity_id}/sitelinks/enwiki"
        )
        assert site_resp.status_code in [200, 404]
