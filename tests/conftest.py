import sys
sys.path.insert(0, "src")

import pytest
from fastapi.testclient import TestClient
from models.rest_api.main import app


@pytest.fixture(scope="session")
def api_client():
    """Return a FastAPI TestClient for testing without starting a server."""
    return TestClient(app)