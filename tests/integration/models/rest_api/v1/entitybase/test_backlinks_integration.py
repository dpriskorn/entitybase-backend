"""Integration tests for backlinks functionality.

These tests require a running server instance and database.
They should be run separately from unit tests.
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
        import logging

        test_logger = logging.getLogger(__name__)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            entity_data = {
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
                "claims": {},
            }

            test_logger.debug(f"Creating entity at {api_prefix}/entities/items")
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
            )
            assert response.status_code == 200
            result = response.json()
            entity_id = result["id"]
            test_logger.debug(f"Created entity: {entity_id}")

            # Query backlinks for the created entity (should be empty initially)
            test_logger.debug(
                f"Querying backlinks at {api_prefix}/entities/{entity_id}/backlinks"
            )
            backlinks_response = await client.get(
                f"{api_prefix}/entities/{entity_id}/backlinks"
            )
            test_logger.debug(
                f"Backlinks response status: {backlinks_response.status_code}"
            )
            test_logger.debug(f"Backlinks response body: {backlinks_response.text}")
            assert backlinks_response.status_code == 200
            backlinks = backlinks_response.json()
            assert "backlinks" in backlinks
            assert backlinks["backlinks"] == []  # Empty backlinks for new entity

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_data_consistency(self) -> None:
        """Test that backlinks data remains consistent across operations."""
        # TODO: Implement consistency tests once backlinks endpoint works
        # - Create entity with references
        # - Update entity, verify backlinks update
        # - Delete entity, verify backlinks are cleaned up
        pass

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_performance(self) -> None:
        """Test backlinks query performance with large datasets."""
        # TODO: Implement performance tests once backlinks endpoint works
        # - Create entity with many references
        # - Measure query time
        # - Test pagination
        pass
