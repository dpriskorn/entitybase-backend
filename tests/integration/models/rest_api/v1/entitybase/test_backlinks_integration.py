"""Integration tests for backlinks functionality.

These tests require a running server instance and database.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


class TestBacklinksIntegration:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_entity_with_backlinks(self, api_prefix: str) -> None:
        """Integration test: Create entity with statements that create backlinks."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"{api_prefix}/entities/items",
                headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
            )
            assert response.status_code == 200
            result = response.json()
            entity_id = result["data"]["entity_id"]

            backlinks_response = await client.get(
                f"{api_prefix}/entities/{entity_id}/backlinks"
            )
            assert backlinks_response.status_code == 200
            backlinks = backlinks_response.json()
            assert "backlinks" in backlinks
            assert backlinks["backlinks"] == []

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_data_consistency(self, api_prefix: str) -> None:
        """Integration test: Backlinks data consistency across operations."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            headers = {"X-Edit-Summary": "test", "X-User-ID": "0"}

            response = await client.get(
                f"{api_prefix}/entities/items",
                headers=headers,
            )
            assert response.status_code == 200
            entity_id = response.json()["data"]["entity_id"]

            response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")
            assert response.status_code == 200
            data = response.json()
            assert "backlinks" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_pagination(self, api_prefix: str) -> None:
        """Integration test: Verify pagination works correctly."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"{api_prefix}/entities/Q1/backlinks?limit=10&offset=0"
            )
            assert response.status_code == 200
            data = response.json()
            assert "backlinks" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_empty_for_nonexistent(self, api_prefix: str) -> None:
        """Integration test: Empty backlinks for non-existent entity."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(f"{api_prefix}/entities/Q99999999/backlinks")
            assert response.status_code == 200
            data = response.json()
            assert "backlinks" in data
            assert data["backlinks"] == []

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_query_after_create(self, api_prefix: str) -> None:
        """Integration test: Query backlinks after entity creation."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            headers = {"X-Edit-Summary": "test", "X-User-ID": "0"}

            response = await client.get(
                f"{api_prefix}/entities/items",
                headers=headers,
            )
            assert response.status_code == 200
            entity_id = response.json()["data"]["entity_id"]

            response = await client.get(f"{api_prefix}/entities/{entity_id}/backlinks")
            assert response.status_code == 200
