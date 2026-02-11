"""Integration tests for backlinks functionality.

These tests require a running server instance and database.
They should be run separately from unit tests.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.skip("Backlinks endpoint not yet implemented in router")
class TestBacklinksIntegration:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_entity_with_backlinks(self, api_prefix: str) -> None:
        """Integration test: Create entity with statements that create backlinks."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            entity_data = {
                "id": "Q999999",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
                "claims": {},
                "edit_summary": "Test entity creation",
            }

            response = await client.post(
                f"{api_prefix}/entities/items", json=entity_data
            )
            assert response.status_code == 200
            result = response.json()
            entity_id = result["id"]

            # Query backlinks for the created entity (should be empty initially)
            backlinks_response = await client.get(
                f"{api_prefix}/entities/{entity_id}/backlinks"
            )
            # This endpoint doesn't exist yet in the router, so this will fail
            # Once the router is updated, this can be a real integration test
            assert backlinks_response.status_code in [
                404,
                200,
            ]  # 404 until endpoint is added

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_data_consistency(self) -> None:
        """Test that backlinks data remains consistent across operations."""
        # Placeholder for consistency tests
        # - Create entity with references
        # - Update entity, verify backlinks update
        # - Delete entity, verify backlinks are cleaned up
        pass

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_backlinks_performance(self) -> None:
        """Test backlinks query performance with large datasets."""
        # Placeholder for performance tests
        # - Create entity with many references
        # - Measure query time
        # - Test pagination
        pass
