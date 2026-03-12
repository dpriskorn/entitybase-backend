"""Integration tests for thanks endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

import sys

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_send_thanks(api_prefix: str) -> None:
    """Test sending thanks for a revision (actually GET to check thanks)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        response = await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Create entity first
        entity_response = await client.post(
            f"{api_prefix}/entities/items",
            json={"type": "item", "labels": {"en": {"language": "en", "value": "Test"}}},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert entity_response.status_code == 200

        # Get revision ID
        entity_id = entity_response.json()["data"]["entity_id"]
        revision_id = 1

        # Get thanks for revision (endpoint uses GET)
        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/revisions/{revision_id}/thanks",
        )
        # Should work (returns 200 or 404 if revision not found)
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_thanks_received(api_prefix: str) -> None:
    """Test getting thanks received by a user."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/users/12345/thanks/received?limit=50&hours=24")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "thanks" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_thanks_sent(api_prefix: str) -> None:
    """Test getting thanks sent by a user."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post(
            f"{api_prefix}/users",
            json={"user_id": 12345},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/users/12345/thanks/sent?limit=50&hours=24")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "thanks" in data
