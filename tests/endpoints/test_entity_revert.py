import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
async def test_revert_entity() -> None:
    """Test reverting an entity to a previous revision"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Note: This test would require a full entity setup with multiple revisions
        # For now, just test that the endpoint accepts requests (will fail without data)
        response = await client.post(
            "/entitybase/v1/entities/Q42/revert",
            json={
                "to_revision_id": 123,
                "reason": "Test revert",
                "reverted_by_user_id": 456,
                "watchlist_context": {"notification_id": 789},
            },
        )
        # Expect 404 or 400 since no test data, but validates request structure
        assert response.status_code in [
            400,
            404,
        ]  # Entity/revision not found is expected in test env


@pytest.mark.asyncio
async def test_revert_entity_invalid_request() -> None:
    """Test revert with invalid request data"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Missing required field
        response = await client.post(
            "/entitybase/v1/entities/Q42/revert",
            json={"reason": "Test revert", "reverted_by_user_id": 456},
        )
        assert response.status_code == 422  # Validation error
