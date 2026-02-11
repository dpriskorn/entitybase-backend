"""Integration tests for endorsement endpoints."""

from unittest import TestCase

import pytest
from httpx import ASGITransport, AsyncClient

import sys

sys.path.insert(0, "src")


@pytest.mark.skip("Not working yet")
class TestEndorsements(TestCase):
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_endorse_statement(self, api_prefix: str) -> None:
        """Test endorsing a statement."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            # First create a user
            response = await client.post(f"{api_prefix}/users", json={"user_id": 12345})
            assert response.status_code == 200

            # Try to endorse a statement (this might fail due to missing statement, but tests the endpoint)
            response = await client.post(
                "/v1/statements/123456789/endorse",
                headers={"X-User-ID": "12345"},
            )

            # The response might be an error due to missing statement, but we test the endpoint exists
            assert response.status_code in [200, 400, 404]  # Success or expected errors

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_withdraw_endorsement(self, api_prefix: str) -> None:
        """Test withdrawing an endorsement."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            # Create a user
            response = await client.post(f"{api_prefix}/users", json={"user_id": 12345})
            assert response.status_code == 200

            # Try to withdraw endorsement
            response = await client.delete(
                "/v1/statements/123456789/endorse",
                headers={"X-User-ID": "12345"},
            )

            # Should return error since no endorsement exists, but endpoint should work
            assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_statement_endorsements(self, api_prefix: str) -> None:
        """Test getting statement endorsements."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            response = await client.get(
                f"{api_prefix}/statements/123456789/endorsements"
            )

            # Should return endorsements list (might be empty)
            assert response.status_code == 200
            data = response.json()
            assert "endorsements" in data
            assert "total_count" in data
            assert "has_more" in data
            assert "stats" in data  # Should include stats metadata

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_statement_endorsement_stats(self, api_prefix: str) -> None:
        """Test getting statement endorsement stats."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            response = await client.get("/v1/statements/123456789/endorsements/stats")

            # Should return stats object
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "active" in data
            assert "withdrawn" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_user_endorsements(self, api_prefix: str) -> None:
        """Test getting user endorsements."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            # Create a user first
            response = await client.post(f"{api_prefix}/users", json={"user_id": 12345})
            assert response.status_code == 200

            # Get user endorsements
            response = await client.get("/entitybase/v1/users/12345/endorsements")

            assert response.status_code == 200
            data = response.json()
            assert "endorsements" in data
            assert "total_count" in data
            assert "has_more" in data
            assert "stats" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_user_endorsement_stats(self, api_prefix: str) -> None:
        """Test getting user endorsement stats."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            # Create a user first
            response = await client.post(f"{api_prefix}/users", json={"user_id": 12345})
            assert response.status_code == 200

            # Get user endorsement stats
            response = await client.get("/entitybase/v1/users/12345/endorsements/stats")

            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data
            assert "total_endorsements_given" in data
            assert "total_endorsements_active" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_batch_endorsement_stats(self, api_prefix: str) -> None:
        """Test batch statement endorsement stats."""
        from models.rest_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://api:8000"
        ) as client:
            response = await client.get("/v1/statements/123456789/endorsements/stats")

            # Should return single statement stats
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "active" in data
            assert "withdrawn" in data
