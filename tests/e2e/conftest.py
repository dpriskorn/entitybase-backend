import os

import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def validate_e2e_env_vars():
    """Validate required environment variables are set before running E2E tests.

    This fixture fails fast if required environment variables are missing,
    preventing long retry loops and confusing connection errors.
    """
    required_vars = {
        "VITESS_HOST": "Vitess database host",
        "VITESS_PORT": "Vitess database port",
        "VITESS_DATABASE": "Vitess database name",
        "VITESS_USER": "Vitess database user",
    }

    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == "":
            missing_vars.append(f"  {var}: {description}")

    if missing_vars:
        error_msg = (
            "Required environment variables are not set:\n"
            + "\n".join(missing_vars)
            + "\n\nPlease set these environment variables before running E2E tests."
        )
        pytest.fail(error_msg)


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
