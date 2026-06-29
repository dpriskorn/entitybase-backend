"""Unit tests for s3_connection."""

from unittest.mock import MagicMock, patch

from models.data.config.s3 import S3Config
from models.infrastructure.s3.connection import S3ConnectionManager


class TestS3ConnectionManager:
    """Unit tests for S3ConnectionManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test_key",
            secret_key="test_secret",
            bucket="test-bucket",
            region="us-east-1",
        )

    def test_connect_already_connected(self):
        """Test connect when already connected."""
        manager = S3ConnectionManager(config=self.config)
        manager.minio_client = MagicMock()

        manager.connect()

        assert manager.minio_client is not None

    @patch("models.infrastructure.s3.connection.logger")
    def test_healthy_connection_success(self, mock_logger):
        """Test healthy connection check success."""
        manager = S3ConnectionManager(config=self.config)
        mock_minio_client = MagicMock()
        manager.minio_client = mock_minio_client

        mock_minio_client.bucket_exists.return_value = True

        result = manager.healthy_connection

        assert result is True
        mock_minio_client.bucket_exists.assert_called_once_with("test-bucket")
        mock_logger.debug.assert_called()

    @patch("models.infrastructure.s3.connection.logger")
    def test_healthy_connection_no_client(self, mock_logger):
        """Test healthy connection when no client exists."""
        manager = S3ConnectionManager(config=self.config)
        manager.minio_client = None

        with patch.object(type(manager), "connect") as mock_connect:
            mock_minio_client = MagicMock()
            manager.minio_client = mock_minio_client
            mock_minio_client.bucket_exists.return_value = True

            result = manager.healthy_connection

            assert result is True
            mock_connect.assert_called_once()

    @patch("models.infrastructure.s3.connection.logger")
    def test_healthy_connection_failure(self, mock_logger):
        """Test healthy connection check failure."""
        manager = S3ConnectionManager(config=self.config)
        mock_minio_client = MagicMock()
        manager.minio_client = mock_minio_client

        mock_minio_client.bucket_exists.side_effect = Exception("Connection failed")

        result = manager.healthy_connection

        assert result is False
        mock_logger.error.assert_called_once()
