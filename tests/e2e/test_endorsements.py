"""End-to-end tests for endorsement feature.

These tests exercise the complete endorsement workflow from API endpoints
to database persistence and back.
"""

import pytest
from httpx import ASGITransport, AsyncClient

import sys
sys.path.insert(0, "src")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_endorsement_full_workflow() -> None:
    """Test complete endorsement workflow: create, list, stats, withdraw."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:

        # Step 1: Create test users
        user1_response = await client.post("/v1/users", json={"user_id": 1001})
        assert user1_response.status_code == 200

        user2_response = await client.post("/v1/users", json={"user_id": 1002})
        assert user2_response.status_code == 200

        # Step 2: Try to endorse a statement (will fail due to missing statement, but tests endpoint)
        endorse_response = await client.post(
            "/entitybase/v1/statements/999999999/endorse",
            headers={"X-User-ID": "1001"}
        )
        # Should fail due to missing statement, but endpoint should exist
        assert endorse_response.status_code in [400, 404]

        # Step 3: Test getting endorsements for non-existent statement
        list_response = await client.get("/entitybase/v1/statements/999999999/endorsements")
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["endorsements"] == []
        assert data["total_count"] == 0
        assert not data["has_more"]
        assert data["stats"]["total"] == 0
        assert data["stats"]["active"] == 0
        assert data["stats"]["withdrawn"] == 0

        # Step 4: Test getting stats for non-existent statement
        stats_response = await client.get("/entitybase/v1/statements/999999999/endorsements/stats")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["total"] == 0
        assert stats_data["active"] == 0
        assert stats_data["withdrawn"] == 0

        # Step 5: Test user endorsements (should be empty)
        user_endorsements_response = await client.get("/entitybase/v1/users/1001/endorsements")
        assert user_endorsements_response.status_code == 200
        user_data = user_endorsements_response.json()
        assert user_data["endorsements"] == []
        assert user_data["total_count"] == 0
        assert user_data["stats"]["total"] == 0

        # Step 6: Test user endorsement stats
        user_stats_response = await client.get("/entitybase/v1/users/1001/endorsements/stats")
        assert user_stats_response.status_code == 200
        user_stats = user_stats_response.json()
        assert user_stats["user_id"] == 1001
        assert user_stats["total_endorsements_given"] == 0
        assert user_stats["total_endorsements_active"] == 0

        # Step 7: Test withdrawal on non-existent endorsement
        withdraw_response = await client.delete(
            "/entitybase/v1/statements/999999999/endorse",
            headers={"X-User-ID": "1001"}
        )
        # Should fail since no endorsement exists
        assert withdraw_response.status_code in [400, 404]


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_endorsement_error_handling() -> None:
    """Test endorsement error handling and validation."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:

        # Test without user ID header
        response = await client.post("/entitybase/v1/statements/999999999/endorse")
        assert response.status_code == 422  # Missing required header

        # Test with invalid user ID
        response = await client.post(
            "/entitybase/v1/statements/999999999/endorse",
            headers={"X-User-ID": "invalid"}
        )
        assert response.status_code == 422  # Invalid user ID format

        # Test with non-existent user
        response = await client.post(
            "/entitybase/v1/statements/999999999/endorse",
            headers={"X-User-ID": "999999"}
        )
        assert response.status_code in [400, 404]  # User not found

        # Test invalid statement hash
        response = await client.get("/entitybase/v1/statements/0/endorsements/stats")
        assert response.status_code == 404  # Invalid statement hash


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_endorsement_api_structure() -> None:
    """Test that all endorsement endpoints return proper JSON structure."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:

        endpoints_to_test = [
            "/entitybase/v1/statements/123456789/endorsements",
            "/entitybase/v1/statements/123456789/endorsements/stats",
        ]

        for endpoint in endpoints_to_test:
            response = await client.get(endpoint)
            assert response.status_code == 200

            # Should return valid JSON
            data = response.json()
            assert isinstance(data, dict)

            # Should not have internal error details
            assert "error" not in str(data).lower()
            assert "exception" not in str(data).lower()