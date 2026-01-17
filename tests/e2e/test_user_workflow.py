import pytest


@pytest.mark.e2e
def test_user_workflow(e2e_api_client, e2e_base_url):
    """E2E test: User registration and watchlist management."""
    base_url = e2e_base_url

    # Register user (assuming API supports)
    user_data = {"username": "e2e_test_user", "email": "test@example.com"}
    response = e2e_api_client.post(f"{base_url}/user", json=user_data)
    if response.status_code == 201:  # If registration succeeds
        user_id = response.json()["user"]["id"]

        # Create entity to watch
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Watch Test Item"}},
        }
        response = e2e_api_client.post(f"{base_url}/entity", json=entity_data)
        assert response.status_code == 200
        entity_id = response.json()["entity"]["id"]

        # Add to watchlist
        watch_data = {"entity_id": entity_id}
        response = e2e_api_client.post(f"{base_url}/user/{user_id}/watchlist", json=watch_data)
        assert response.status_code == 200

        # Verify watchlist
        response = e2e_api_client.get(f"{base_url}/user/{user_id}/watchlist")
        assert response.status_code == 200
        watchlist = response.json()
        assert entity_id in [w["entity_id"] for w in watchlist["watches"]]

        # Remove from watchlist
        response = e2e_api_client.delete(f"{base_url}/user/{user_id}/watchlist/{entity_id}")
        assert response.status_code == 200

        # Verify removal
        response = e2e_api_client.get(f"{base_url}/user/{user_id}/watchlist")
        assert response.status_code == 200
        watchlist = response.json()
        assert entity_id not in [w["entity_id"] for w in watchlist["watches"]]
    else:
        pytest.skip("User registration not supported or already exists")