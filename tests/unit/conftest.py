import os
import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from models.rdf_builder.ontology.datatypes import property_shape
from models.rdf_builder.property_registry.registry import PropertyRegistry

sys.path.insert(0, "src")
os.environ["TEST_DATA_DIR"] = str(Path(__file__).parent.parent.parent / "test_data")

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
    from models.rest_api.main import app


@pytest.fixture(scope="session")
def db_url():
    """Determine DB URL based on test type."""
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


@pytest.fixture
def validator():
    """Return a JsonSchemaValidator for testing."""
    from models.validation.json_schema_validator import JsonSchemaValidator

    return JsonSchemaValidator()


@pytest.fixture(autouse=True)
def mock_aiokafka():
    """Mock aiokafka to prevent real Kafka connections in tests."""
    with patch("aiokafka.AIOKafkaConsumer", new_callable=AsyncMock) as mock_consumer:
        with patch(
            "aiokafka.AIOKafkaProducer", new_callable=AsyncMock
        ) as mock_producer:
            yield mock_consumer, mock_producer


@pytest.fixture(scope="session", autouse=True)
def mock_pymysql_connect():
    """Mock pymysql.connect to prevent real database connections in unit tests.

    This patch ensures that VitessClient and related infrastructure components
    don't attempt to connect to a real MySQL database during unit testing.
    Integration tests should use the real database connection.
    """
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.__enter__ = MagicMock(return_value=mock_connection)
    mock_connection.__exit__ = MagicMock(return_value=None)

    with patch("pymysql.connect", return_value=mock_connection):
        yield


@pytest.fixture
def mock_vitess_connection_manager():
    """Mock VitessConnectionManager to prevent pool operations.

    This fixture patches the connect and acquire methods to return a mock connection,
    preventing the connection manager from attempting real database connections
    or pool operations during unit tests.
    """
    from models.infrastructure.vitess.connection import VitessConnectionManager

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.open = True
    mock_connection.__enter__ = MagicMock(return_value=mock_connection)
    mock_connection.__exit__ = MagicMock(return_value=None)

    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=None)

    with patch.object(VitessConnectionManager, "connect", return_value=mock_connection):
        with patch.object(
            VitessConnectionManager, "acquire", return_value=mock_connection
        ):
            yield mock_connection, mock_cursor


@pytest.fixture
def property_registry() -> PropertyRegistry:
    """Minimal property registry for Q120248304 test."""
    properties = {
        "P31": property_shape(
            "P31",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "instance of"}},
        ),
        "P17": property_shape(
            "P17",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "country"}},
        ),
        "P127": property_shape(
            "P127",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "owned by"}},
        ),
        "P131": property_shape(
            "P131",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "located in"}},
        ),
        "P137": property_shape(
            "P137",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "operator"}},
        ),
        "P912": property_shape(
            "P912",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "sponsor"}},
        ),
        "P248": property_shape(
            "P248",
            "wikibase-item",
            labels={"en": {"language": "en", "value": "stated in"}},
        ),
        "P11840": property_shape(
            "P11840",
            "external-id",
            labels={"en": {"language": "en", "value": "crossref ID"}},
        ),
        "P1810": property_shape(
            "P1810", "string", labels={"en": {"language": "en", "value": "short name"}}
        ),
        "P2561": property_shape(
            "P2561",
            "monolingualtext",
            labels={"en": {"language": "en", "value": "description"}},
        ),
        "P5017": property_shape(
            "P5017",
            "time",
            labels={"en": {"language": "en", "value": "date of official opening"}},
        ),
        "P625": property_shape(
            "P625",
            "globe-coordinate",
            labels={"en": {"language": "en", "value": "coordinate location"}},
        ),
        "P6375": property_shape(
            "P6375",
            "monolingualtext",
            labels={"en": {"language": "en", "value": "street address"}},
        ),
    }
    return PropertyRegistry(properties=properties)
