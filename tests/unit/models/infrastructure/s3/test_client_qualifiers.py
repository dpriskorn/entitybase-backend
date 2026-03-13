"""Unit tests for S3 client qualifier methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientQualifiers:
    """Unit tests for S3 client qualifier methods."""

    def test_store_qualifier_success(self):
        """Test successful qualifier storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_qualifiers = MagicMock()
            client.vitess_qualifiers.store_qualifier.return_value = MagicMock(
                success=True
            )

            qual_data = S3QualifierData(
                qualifier={"id": "q1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )
            client.store_qualifier(12345, qual_data)

            client.vitess_qualifiers.store_qualifier.assert_called_once()

    def test_load_qualifier_success(self):
        """Test successful qualifier load."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_qualifiers = MagicMock()

            client.vitess_qualifiers.load_qualifier.return_value = S3QualifierData(
                qualifier={"id": "q1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )

            result = client.load_qualifier(12345)

            assert result.content_hash == 12345

    def test_load_qualifiers_batch(self):
        """Test loading qualifiers batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_qualifiers = MagicMock()
            client.vitess_qualifiers.load_qualifiers_batch.return_value = [
                None,
                {"id": "q2"},
            ]

            result = client.load_qualifiers_batch([111, 222])

            assert len(result) == 2
