import pytest
import requests
from tenacity import retry, stop_after_attempt, wait_exponential


@pytest.fixture(scope="session")
def e2e_api_client():
    """API client for E2E tests - connects to running application."""
    base_url = "http://api:8000"  # Adjust for Docker container URL

    # Wait for API to be ready
    @retry(
        stop=stop_after_attempt(30), wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def wait_for_api():
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            response.raise_for_status()
            assert response.json().get("status") == "ok"
        except requests.RequestException:
            raise Exception("E2E API not ready")

    wait_for_api()
    return requests.Session()


@pytest.fixture(scope="session")
def e2e_base_url():
    """Base URL for E2E API."""
    return "http://api:8000"
