import os
import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, "src")
os.environ["TEST_DATA_DIR"] = str(Path(__file__).parent.parent.parent / "test_data")

# Mock S3 and DB before importing app to prevent connection attempts
with (
    patch("boto3.client") as mock_boto_client,
    patch("pymysql.connect") as mock_db_connect,
    patch(
        "models.infrastructure.s3.connection.S3ConnectionManager.connect"
    ) as mock_s3_connect,
):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.head_bucket.return_value = None  # Assume bucket exists
    mock_client.create_bucket.return_value = None
    mock_conn = MagicMock()
    mock_db_connect.return_value = mock_conn
    mock_s3_connect.return_value = None
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


@pytest.fixture
def mock_kafka_consumer():
    """Mock Kafka consumer"""
    mock_consumer = AsyncMock()
    mock_consumer.start = AsyncMock()
    mock_consumer.stop = AsyncMock()
    mock_consumer.__aenter__ = AsyncMock(return_value=mock_consumer)
    mock_consumer.__aexit__ = AsyncMock(return_value=None)
    return mock_consumer


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer"""
    mock_producer = MagicMock()
    mock_producer.start = AsyncMock()
    mock_producer.stop = AsyncMock()
    mock_producer.send_and_wait = AsyncMock()
    return mock_producer


@pytest.fixture(autouse=True)
def mock_aiokafka():
    """Mock aiokafka to prevent real Kafka connections in tests."""
    with patch("aiokafka.AIOKafkaConsumer", new_callable=AsyncMock) as mock_consumer:
        with patch(
            "aiokafka.AIOKafkaProducer", new_callable=AsyncMock
        ) as mock_producer:
            yield mock_consumer, mock_producer
