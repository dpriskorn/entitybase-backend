import pytest
import pymysql
import time
from unittest.mock import AsyncMock, MagicMock
from moto import mock_aws as mock_s3


@pytest.fixture(scope="session")
def db_conn():
    """Database connection for cleanup"""
    # Wait for DB to be ready
    max_retries = 30
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host="vitess", port=15309, user="root", password="", database="entitybase"
            )
            # Test connection with a simple query
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            break
        except pymysql.Error as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def db_cleanup(db_conn):
    yield
    # Truncate relevant tables after each test
    tables = [
        "entity_revisions",
        "entity_head",
        "metadata_content",
        "entity_backlinks",
        "backlink_statistics",
    ]
    with db_conn.cursor() as cursor:
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
    db_conn.commit()


@pytest.fixture(autouse=True)
def mock_s3_service():
    """Mock S3 service for all integration tests"""
    with mock_s3():
        # Create a mock bucket
        import boto3

        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="testbucket")
        yield


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
