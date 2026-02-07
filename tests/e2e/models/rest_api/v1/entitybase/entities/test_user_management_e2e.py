"""E2E tests for user management operations."""

import pytest


@pytest.mark.e2e
def test_create_user(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Create a new user."""
    user_data = {"user_id": 90001}
    response = e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 90001


@pytest.mark.e2e
def test_get_user_stats(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get user statistics."""
    # Create user first
    user_data = {"user_id": 90002}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Get stats
    response = e2e_api_client.get(f"{e2e_base_url}/users/stat")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data or "count" in data


@pytest.mark.e2e
def test_get_user_info(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get user information by MediaWiki user ID."""
    # Create user first
    user_data = {"user_id": 90003}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Get user info
    response = e2e_api_client.get(f"{e2e_base_url}/users/90003")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 90003


@pytest.mark.e2e
def test_get_user_endorsements(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get endorsements given by a user."""
    # Create user first
    user_data = {"user_id": 90004}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Get user endorsements
    response = e2e_api_client.get(
        f"{e2e_base_url}/users/90004/endorsements?limit=10&offset=0"
    )
    assert response.status_code == 200
    data = response.json()
    assert "endorsements" in data
    assert "total_count" in data


@pytest.mark.e2e
def test_get_user_endorsement_stats(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get endorsement statistics for a user."""
    # Create user first
    user_data = {"user_id": 90005}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Get user endorsement stats
    response = e2e_api_client.get(f"{e2e_base_url}/users/90005/endorsements/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 90005
    assert "total_endorsements_given" in data
    assert "total_endorsements_active" in data
