"""Unit tests for S3 client snak methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.data.infrastructure.s3.snak_data import S3SnakData
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientSnaks:
    """Unit tests for S3 client snak methods."""

    def test_store_snak_success(self):
        """Test successful snak storage."""
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
            client.vitess_snaks = MagicMock()
            client.vitess_snaks.store_snak.return_value = MagicMock(success=True)

            snak_data = S3SnakData(
                snak={"id": "s1"},
                hash=12345,
                schema="1.0.0",
                created_at="2023-01-01T12:00:00Z",
            )
            client.store_snak(12345, snak_data)

            client.vitess_snaks.store_snak.assert_called_once()

    def test_load_snak_success(self):
        """Test successful snak load."""
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
            client.vitess_snaks = MagicMock()

            client.vitess_snaks.load_snak.return_value = S3SnakData(
                snak={"id": "s1"},
                hash=12345,
                schema="1.0.0",
                created_at="2023-01-01T12:00:00Z",
            )

            result = client.load_snak(12345)

            assert result.content_hash == 12345

    def test_load_snaks_batch(self):
        """Test loading snaks batch."""
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
            client.vitess_snaks = MagicMock()
            client.vitess_snaks.load_snaks_batch.return_value = [None, {"id": "s2"}]

            result = client.load_snaks_batch([111, 222])

            assert len(result) == 2

    def test_store_snak_not_configured(self):
        """Test store_snak raises error when Vitess not configured."""
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

            snak_data = S3SnakData(
                snak={"id": "s1"},
                hash=12345,
                schema="1.0.0",
                created_at="2023-01-01T12:00:00Z",
            )
            with pytest.raises(Exception):
                client.store_snak(12345, snak_data)

    def test_store_snak_failure(self):
        """Test store_snak raises error when storage fails."""
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
            client.vitess_snaks = MagicMock()
            client.vitess_snaks.store_snak.return_value = MagicMock(
                success=False, error="Database error"
            )

            snak_data = S3SnakData(
                snak={"id": "s1"},
                hash=12345,
                schema="1.0.0",
                created_at="2023-01-01T12:00:00Z",
            )
            with pytest.raises(Exception):
                client.store_snak(12345, snak_data)

    def test_load_snak_not_configured(self):
        """Test load_snak raises error when Vitess not configured."""
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
                client.load_snak(12345)

    def test_load_snak_not_found(self):
        """Test load_snak raises error when snak not found."""
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
            client.vitess_snaks = MagicMock()
            client.vitess_snaks.load_snak.return_value = None

            with pytest.raises(Exception):
                client.load_snak(12345)

    def test_load_snaks_batch_not_configured(self):
        """Test load_snaks_batch raises error when Vitess not configured."""
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
                client.load_snaks_batch([111, 222])
