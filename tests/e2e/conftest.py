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
