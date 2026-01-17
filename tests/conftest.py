import sys
sys.path.insert(0, "src")

import pytest
from fastapi.testclient import TestClient
from models.rest_api.main import app


@pytest.fixture(scope="session")
def db_url():
    """Determine DB URL based on test type."""
    import os
    # Check if running integration tests (presence of integration in path or env)
    if os.getenv("TEST_TYPE") == "integration" or "integration" in os.getcwd():
        return "mysql://root@vitess:15309/page"
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def api_client():
    """Return a FastAPI TestClient for testing without starting a server."""
    return TestClient(app)