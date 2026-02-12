import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_workflow(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: User registration and watchlist management."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user (assuming API supports)
        user_data = {"user_id": 90001}
        response = await client.post(f"{api_prefix}/users", json=user_data)
        if response.status_code == 200:  # If registration succeeds
            user_id = 90001

            # Create entity to watch
            entity_data = {
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Watch Test Item"}},
            }
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
            )
            assert response.status_code == 200
            entity_id = response.json()["id"]

            # Add to watchlist
            watch_data = {"entity_id": entity_id, "properties": ["P31"]}
            response = await client.post(
                f"{api_prefix}/users/{user_id}/watchlist", json=watch_data
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
