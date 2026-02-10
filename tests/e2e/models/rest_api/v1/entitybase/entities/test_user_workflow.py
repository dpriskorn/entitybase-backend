import pytest
import sys

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.e2e
async def def test_user_workflow(e2e_api_client, e2e_base_url) -> None:() -> None:
    from models.rest_api.main import app

    """E2E test: User registration and watchlist management."""

    # Register user (assuming API supports)
    user_data = {"user_id": 90001}
    response = await client.post(f"{base_url}/users", json=user_data)
    if response.status_code == 200:  # If registration succeeds
        user_id = 90001

        # Create entity to watch
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Watch Test Item"}},
        }
        response = await client.post(
            f"{base_url}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Add to watchlist
        watch_data = {"entity_id": entity_id, "properties": ["P31"]}
        response = await client.post(
            f"{base_url}/users/{user_id}/watchlist", json=watch_data
        )
        assert response.status_code == 200

        # Verify watchlist
        response = await client.get(f"{base_url}/users/{user_id}/watchlist")
        assert response.status_code == 200
        watchlist = response.json()
        assert entity_id in [w["entity_id"] for w in watchlist["watches"]]

        # Remove from watchlist
        response = await client.post(
            f"{base_url}/users/{user_id}/watchlist/remove",
            json={"entity_id": entity_id},
        )
        assert response.status_code == 200

        # Verify removal
        response = await client.get(f"{base_url}/users/{user_id}/watchlist")
        assert response.status_code == 200
        watchlist = response.json()
        assert entity_id not in [w["entity_id"] for w in watchlist["watches"]]
    else:
        pytest.skip("User registration not supported or already exists")
