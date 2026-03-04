import pytest
import sys
import time

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_workflow(api_prefix: str) -> None:
    import logging
    from models.rest_api.main import app
    from tests.e2e.conftest import get_entity_id_from_response

    logger = logging.getLogger(__name__)

    """E2E test: User registration and watchlist management."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Use unique user ID to avoid conflicts with previous test runs
        unique_user_id = int(time.time() * 1000) % 100000000
        user_data = {"user_id": unique_user_id}
        response = await client.post(f"{api_prefix}/users", json=user_data)
        logger.error(
            f"User creation response: {response.status_code} - {response.text}"
        )
        if response.status_code == 200:  # If registration succeeds
            user_id = unique_user_id

            # Create entity to watch
            response = await client.get(
                f"{api_prefix}/entities/items",
                headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
            )
            entity_id = get_entity_id_from_response(response)

            # Add to watchlist
            watch_data = {"entity_id": entity_id, "properties": ["P31"]}
            response = await client.post(
                f"{api_prefix}/users/{user_id}/watchlist", json=watch_data
            )
            logger.error(
                f"Add watch response: {response.status_code} - {response.text}"
            )
            assert response.status_code == 200

            # Verify watchlist
            response = await client.get(f"{api_prefix}/users/{user_id}/watchlist")
            assert response.status_code == 200
            watchlist = response.json()
            assert entity_id in [w["entity_id"] for w in watchlist["watches"]]

            # Remove from watchlist
            response = await client.post(
                f"{api_prefix}/users/{user_id}/watchlist/remove",
                json={"entity_id": entity_id},
            )
            assert response.status_code == 200

            # Verify removal
            response = await client.get(f"{api_prefix}/users/{user_id}/watchlist")
            assert response.status_code == 200
            watchlist = response.json()
            assert entity_id not in [w["entity_id"] for w in watchlist["watches"]]
        else:
            pytest.skip("User registration not supported or already exists")
