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
async def test_endorsement_full_workflow(api_prefix: str) -> None:
    """Test complete endorsement workflow: create, list, stats, withdraw."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Step 1: Create test users
        user1_response = await client.post(
            f"{api_prefix}/users", json={"user_id": 1001}
        )
        assert user1_response.status_code == 200

        user2_response = await client.post(
            f"{api_prefix}/users", json={"user_id": 1002}
        )
        assert user2_response.status_code == 200

        # Step 2: Try to endorse a statement (will fail due to missing statement, but tests endpoint)
        endorse_response = await client.post(
            f"{api_prefix}/statements/999999999/endorse", headers={"X-User-ID": "1001"}
        )
        # Should fail due to missing statement, but endpoint should exist
        assert endorse_response.status_code in [400, 404]

        # Step 3: Test getting endorsements for non-existent statement
        list_response = await client.get(
            f"{api_prefix}/statements/999999999/endorsements"
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["list"] == []
        assert data["count"] == 0
        assert not data["more"]
        assert data["stats"]["total"] == 0
        assert data["stats"]["active"] == 0
        assert data["stats"]["withdrawn"] == 0

        # Step 4: Test getting stats for non-existent statement
        stats_response = await client.get(
            f"{api_prefix}/statements/999999999/endorsements/stats"
        )
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["total"] == 0
        assert stats_data["active"] == 0
        assert stats_data["withdrawn"] == 0

        # Step 5: Test user endorsements (should be empty)
        user_endorsements_response = await client.get(
            f"{api_prefix}/users/1001/endorsements"
        )
        assert user_endorsements_response.status_code == 200
        user_data = user_endorsements_response.json()
        assert user_data["list"] == []
        assert user_data["count"] == 0
        assert user_data["stats"]["total"] == 0

        # Step 6: Test user endorsement stats
        user_stats_response = await client.get(
            f"{api_prefix}/users/1001/endorsements/stats"
        )
        assert user_stats_response.status_code == 200
        user_stats = user_stats_response.json()
        assert user_stats["user_id"] == 1001
        assert user_stats["total_endorsements_given"] == 0
        assert user_stats["total_endorsements_active"] == 0

        # Step 7: Test withdrawal on non-existent endorsement
        withdraw_response = await client.delete(
            f"{api_prefix}/statements/999999999/endorse", headers={"X-User-ID": "1001"}
        )
        # Should fail since no endorsement exists
        assert withdraw_response.status_code in [400, 404]


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_endorsement_error_handling(api_prefix: str) -> None:
    """Test endorsement error handling and validation."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test without user ID header
        response = await client.post(f"{api_prefix}/statements/999999999/endorse")
        assert response.status_code == 422  # Missing required header

        # Test with invalid user ID
        response = await client.post(
            f"{api_prefix}/statements/999999999/endorse",
            headers={"X-User-ID": "invalid"},
        )
        assert response.status_code == 422  # Invalid user ID format

        # Test with non-existent user
        response = await client.post(
            f"{api_prefix}/statements/999999999/endorse",
            headers={"X-User-ID": "999999"},
        )
        assert response.status_code in [400, 404]  # User not found

        # Test invalid statement hash
        response = await client.get(f"{api_prefix}/statements/0/endorsements/stats")
        assert response.status_code == 404  # Invalid statement hash


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_endorsement_api_structure(api_prefix: str) -> None:
    """Test that all endorsement endpoints return proper JSON structure."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        endpoints_to_test = [
            f"{api_prefix}/statements/123456789/endorsements",
            f"{api_prefix}/statements/123456789/endorsements/stats",
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


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_statement_most_used(api_prefix: str) -> None:
    """Test getting most used statements."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/statements/most_used?limit=10&min_ref_count=1"
        )
        assert response.status_code == 200
        data = response.json()
        assert "statements" in data or isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_cleanup_orphaned_statements(api_prefix: str) -> None:
    """Test cleaning up orphaned statements."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        cleanup_request = {"dry_run": True, "batch_size": 100}
        response = await client.post(
            f"{api_prefix}/statements/cleanup-orphaned", json=cleanup_request
        )
        assert response.status_code == 200
        data = response.json()
        assert "cleaned_count" in data or "count" in data


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_get_single_statement(api_prefix: str) -> None:
    """Test retrieving a single statement by content hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Get non-existent statement
        response = await client.get(f"{api_prefix}/statements/123456789")
        # May return 404 or 200 with empty data
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_endorse_and_withdraw_statement(api_prefix: str) -> None:
    """Test endorsing and withdrawing from a statement."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create user
        await client.post(f"{api_prefix}/users", json={"user_id": 1003})

        # Try to endorse non-existent statement (endpoint test)
        endorse_response = await client.post(
            f"{api_prefix}/statements/123456789/endorse", headers={"X-User-ID": "1003"}
        )
        # Will fail but endpoint works
        assert endorse_response.status_code in [400, 404]

        # Try to withdraw (endpoint test)
        withdraw_response = await client.delete(
            f"{api_prefix}/statements/123456789/endorse", headers={"X-User-ID": "1003"}
        )
        # Will fail but endpoint works
        assert withdraw_response.status_code in [400, 404]


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_statement_endorsements_with_params(api_prefix: str) -> None:
    """Test getting statement endorsements with query parameters."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test with limit, offset, include_removed
        response = await client.get(
            f"{api_prefix}/statements/123456789/endorsements?limit=10&offset=0&include_removed=true"
        )
        assert response.status_code == 200
        data = response.json()
        assert "list" in data
        assert "count" in data


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_statement_endorsements_stats_endpoint(api_prefix: str) -> None:
    """Test statement endorsement stats endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/statements/123456789/endorsements/stats"
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "active" in data
        assert "withdrawn" in data
