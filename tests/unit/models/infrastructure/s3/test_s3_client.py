"""Unit tests for S3 client."""

import pytest

from models.data.config.s3 import S3Config
from models.infrastructure.s3.client import MyS3Client


class TestMyS3Client:
    """Unit tests for MyS3Client."""

    def test_client_initialization(self):
        """Test client initializes with config."""
        config = S3Config(
            endpoint_url="http://localhost",
            access_key="access_key",
            secret_key="secret_key",
            bucket="bucket",
            region="region",
        )
        client = MyS3Client(config=config)
        assert client.config == config

    def test_client_has_connection_manager_attribute(self):
        """Test client has connection_manager attribute after init."""
        config = S3Config(
            endpoint_url="http://localhost",
            access_key="access_key",
            secret_key="secret_key",
            bucket="bucket",
            region="region",
        )
        client = MyS3Client(config=config)
        assert hasattr(client, "connection_manager")
