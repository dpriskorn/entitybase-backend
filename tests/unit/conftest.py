import os
import sys
from pathlib import Path

sys.path.insert(0, "src")
os.environ["TEST_DATA_DIR"] = str(Path(__file__).parent.parent.parent / "test_data")

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Mock S3 and DB before importing app to prevent connection attempts
with (
    patch("boto3.client") as mock_boto_client,
    patch("pymysql.connect") as mock_db_connect,
):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.head_bucket.return_value = None  # Assume bucket exists
    mock_client.create_bucket.return_value = None
    mock_conn = MagicMock()
    mock_db_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = MagicMock()
    mock_conn.cursor.return_value.__exit__.return_value = None
    from models.rest_api.main import app

from fastapi.testclient import TestClient


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
