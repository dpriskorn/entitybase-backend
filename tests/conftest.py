import sys
from pathlib import Path
import os

sys.path.insert(0, "src")
os.environ["TEST_DATA_DIR"] = str(Path(__file__).parent.parent / "test_data")

import pytest
from unittest.mock import AsyncMock, patch
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


@pytest.fixture(autouse=True)
def mock_aiokafka():
    """Mock aiokafka to prevent real Kafka connections in tests."""
    with patch("aiokafka.AIOKafkaConsumer", new_callable=AsyncMock) as mock_consumer:
        with patch(
            "aiokafka.AIOKafkaProducer", new_callable=AsyncMock
        ) as mock_producer:
            yield mock_consumer, mock_producer
