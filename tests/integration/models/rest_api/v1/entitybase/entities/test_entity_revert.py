import sys
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revert_entity() -> None:
    """Test reverting an entity to a previous revision"""
    from models.rest_api.main import app

    # Mock app.state.state_handler since lifespan startup doesn't run with ASGITransport
    mock_clients = MagicMock()
    app.state.state_handler = mock_clients

    # Set up mocks to simulate missing entity
    mock_clients.vitess.id_resolver.resolve_id.return_value = 0

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Note: This test would require a full entity setup with multiple revisions
        # For now, just test that the endpoint accepts requests (will fail without data)
        response = await client.post(
            "/entitybase/v1/entities/Q42/revert",
            headers={"X-Edit-Summary": "test revert", "X-User-ID": "456"},
            json={
                "to_revision_id": 123,
                "edit_summary": "Test revert",
                "watchlist_context": {"notification_id": 789},
            },
        )
        # Expect 404 or 400 since no test data, but validates request structure
        assert response.status_code in [
            400,
            404,
        ]  # Entity/revision not found is expected in test env


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revert_entity_missing_user_header() -> None:
    """Test revert without user ID header"""
    from models.rest_api.main import app

    # Mock app.state.state_handler since lifespan startup doesn't run with ASGITransport
    mock_clients = MagicMock()
    app.state.state_handler = mock_clients

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/entitybase/v1/entities/Q42/revert",
            json={"to_revision_id": 123, "edit_summary": "Test revert"},
        )
        assert response.status_code == 422  # Missing required header


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revert_entity_invalid_user_header() -> None:
    """Test revert with invalid user ID header"""
    from models.rest_api.main import app

    # Mock app.state.state_handler since lifespan startup doesn't run with ASGITransport
    mock_clients = MagicMock()
    app.state.state_handler = mock_clients

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/entitybase/v1/entities/Q42/revert",
            headers={"X-Edit-Summary": "invalid user test", "X-User-ID": "0"},
            json={"to_revision_id": 123, "edit_summary": "Test revert"},
        )
        assert response.status_code == 400  # Invalid user ID


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revert_entity_invalid_request() -> None:
    """Test revert with invalid request data"""
    from models.rest_api.main import app

    # Mock app.state.state_handler since lifespan startup doesn't run with ASGITransport
    mock_clients = MagicMock()
    app.state.state_handler = mock_clients

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Missing required field
        response = await client.post(
            "/entitybase/v1/entities/Q42/revert",
            headers={"X-Edit-Summary": "invalid request test", "X-User-ID": "456"},
            json={"edit_summary": "Test revert"},
        )
        assert response.status_code == 422  # Validation error
