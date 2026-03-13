"""Unit tests for S3 client reference methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientReferences:
    """Unit tests for S3 client reference methods."""

    def test_store_reference_success(self):
        """Test successful reference storage."""
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
            client.vitess_references = MagicMock()
            client.vitess_references.store_reference.return_value = MagicMock(
                success=True
            )

            ref_data = S3ReferenceData(
                reference={"id": "ref1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )
            client.store_reference(12345, ref_data)

            client.vitess_references.store_reference.assert_called_once()

    def test_load_reference_success(self):
        """Test successful reference load."""
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
            client.vitess_references = MagicMock()

            client.vitess_references.load_reference.return_value = S3ReferenceData(
                reference={"id": "ref1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )

            result = client.load_reference(12345)

            assert result.content_hash == 12345

    def test_load_references_batch(self):
        """Test loading references batch."""
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
            client.vitess_references = MagicMock()
            client.vitess_references.load_references_batch.return_value = [
                None,
                {"id": "ref2"},
            ]

            result = client.load_references_batch([111, 222])

            assert len(result) == 2
            assert result[0] is None

    def test_store_reference_not_configured(self):
        """Test store_reference raises error when Vitess not configured."""
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=MagicMock(),
        ):
            client = MyS3Client(config=config)

            ref_data = S3ReferenceData(
                reference={"id": "ref1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )
            with pytest.raises(Exception):
                client.store_reference(12345, ref_data)

    def test_store_reference_failure(self):
        """Test store_reference raises error when storage fails."""
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
            client.vitess_references = MagicMock()
            client.vitess_references.store_reference.return_value = MagicMock(
                success=False, error="Database error"
            )

            ref_data = S3ReferenceData(
                reference={"id": "ref1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )
            with pytest.raises(Exception):
                client.store_reference(12345, ref_data)

    def test_load_reference_not_configured(self):
        """Test load_reference raises error when Vitess not configured."""
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=MagicMock(),
        ):
            client = MyS3Client(config=config)

            with pytest.raises(Exception):
                client.load_reference(12345)

    def test_load_reference_not_found(self):
        """Test load_reference raises error when reference not found."""
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
            client.vitess_references = MagicMock()
            client.vitess_references.load_reference.return_value = None

            with pytest.raises(Exception):
                client.load_reference(12345)

    def test_load_references_batch_not_configured(self):
        """Test load_references_batch raises error when Vitess not configured."""
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=MagicMock(),
        ):
            client = MyS3Client(config=config)

            with pytest.raises(Exception):
                client.load_references_batch([111, 222])
