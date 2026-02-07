import pytest
import requests


@pytest.fixture(scope="session")
def e2e_api_client():
    """API client for E2E tests - connects to running application."""
    base_url = "http://api:8000"  # Adjust for Docker container URL
    return requests.Session()


@pytest.fixture(scope="session")
def e2e_base_url():
    """Base URL for E2E API."""
    return "http://api:8000"


@pytest.fixture(scope="session")
def create_entity_helper(e2e_api_client, e2e_base_url):
    """Helper fixture to create entities and return entity ID."""

    def _create(entity_data):
        response = e2e_api_client.post(
            f"{e2e_base_url}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "E2E test setup", "X-User-ID": "0"},
        )
        if response.status_code == 200:
            return response.json()["id"]
        return None

    return _create
