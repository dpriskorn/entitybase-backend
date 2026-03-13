"""Unit tests for S3 client metadata methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.data.infrastructure.s3.enums import MetadataType
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientMetadata:
    """Unit tests for S3 client metadata methods."""

    def test_store_term_metadata_success(self):
        """Test successful term metadata storage."""
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
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.store_metadata.return_value = MagicMock(success=True)

            client.store_term_metadata("Test", 12345, "labels")

            client.vitess_metadata.store_metadata.assert_called_once()

    def test_load_metadata_success(self):
        """Test successful metadata load."""
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
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_metadata.return_value = "Test value"

            result = client.load_metadata(MetadataType.LABELS, 12345)

            assert result is not None
            assert result.data == "Test value"

    def test_load_metadata_not_found(self):
        """Test load_metadata returns None when not found."""
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
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_metadata.return_value = None

            result = client.load_metadata(MetadataType.LABELS, 12345)

            assert result is None

    def test_store_sitelink_metadata_success(self):
        """Test successful sitelink metadata storage."""
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
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.store_sitelink.return_value = MagicMock(
                success=True
            )

            client.store_sitelink_metadata("Main_Page", 12345)

            client.vitess_sitelinks.store_sitelink.assert_called_once()

    def test_load_sitelink_metadata_success(self):
        """Test successful sitelink metadata load."""
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
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.load_sitelink.return_value = "Main_Page"

            result = client.load_sitelink_metadata(12345)

            assert result == "Main_Page"

    def test_load_sitelink_metadata_not_configured(self):
        """Test load_sitelink_metadata raises error when Vitess not configured."""
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
                client.load_sitelink_metadata(12345)

    def test_load_sitelink_metadata_not_found(self):
        """Test load_sitelink_metadata raises error when not found."""
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
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.load_sitelink.return_value = None

            with pytest.raises(Exception):
                client.load_sitelink_metadata(12345)

    def test_delete_metadata_success(self):
        """Test successful metadata deletion."""
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
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.delete_metadata.return_value = MagicMock(
                success=True
            )

            client.delete_metadata(MetadataType.LABELS, 12345)

            client.vitess_metadata.delete_metadata.assert_called_once()

    def test_delete_metadata_not_configured(self):
        """Test delete_metadata raises error when Vitess not configured."""
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
                client.delete_metadata(MetadataType.LABELS, 12345)

    def test_delete_metadata_failure(self):
        """Test delete_metadata raises error when storage fails."""
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
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.delete_metadata.return_value = MagicMock(
                success=False, error="Database error"
            )

            with pytest.raises(Exception):
                client.delete_metadata(MetadataType.LABELS, 12345)

    def test_store_term_metadata_not_configured(self):
        """Test store_term_metadata raises error when Vitess not configured."""
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
                client.store_term_metadata("Test", 12345, "labels")

    def test_store_term_metadata_failure(self):
        """Test store_term_metadata raises error when storage fails."""
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
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.store_metadata.return_value = MagicMock(
                success=False, error="Database error"
            )

            with pytest.raises(Exception):
                client.store_term_metadata("Test", 12345, "labels")

    def test_load_metadata_not_configured(self):
        """Test load_metadata raises error when Vitess not configured."""
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
                client.load_metadata(MetadataType.LABELS, 12345)

    def test_store_sitelink_metadata_not_configured(self):
        """Test store_sitelink_metadata raises error when Vitess not configured."""
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
                client.store_sitelink_metadata("Main_Page", 12345)

    def test_store_sitelink_metadata_failure(self):
        """Test store_sitelink_metadata raises error when storage fails."""
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
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.store_sitelink.return_value = MagicMock(
                success=False, error="Database error"
            )

            with pytest.raises(Exception):
                client.store_sitelink_metadata("Main_Page", 12345)
