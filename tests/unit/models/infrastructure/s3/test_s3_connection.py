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
        manager.boto_client = MagicMock()

        manager.connect()

        # Should not create new client
        assert manager.boto_client is not None

    @patch("models.infrastructure.s3.connection.logger")
    def test_healthy_connection_success(self, mock_logger):
        """Test healthy connection check success."""
        manager = S3ConnectionManager(config=self.config)
        mock_boto_client = MagicMock()
        manager.boto_client = mock_boto_client

        mock_boto_client.head_bucket.return_value = {}

        result = manager.healthy_connection

        assert result is True
        mock_boto_client.head_bucket.assert_called_once_with(Bucket="test-bucket")
        mock_logger.debug.assert_called()

    @patch("models.infrastructure.s3.connection.logger")
    def test_healthy_connection_no_client(self, mock_logger):
        """Test healthy connection when no client exists."""
        manager = S3ConnectionManager(config=self.config)
        manager.boto_client = None

        with patch.object(type(manager), "connect") as mock_connect:
            mock_boto_client = MagicMock()
            manager.boto_client = mock_boto_client
            mock_boto_client.head_bucket.return_value = {}

            result = manager.healthy_connection

            assert result is True
            mock_connect.assert_called_once()

    @patch("models.infrastructure.s3.connection.logger")
    def test_healthy_connection_failure(self, mock_logger):
        """Test healthy connection check failure."""
        manager = S3ConnectionManager(config=self.config)
        mock_boto_client = MagicMock()
        manager.boto_client = mock_boto_client

        mock_boto_client.head_bucket.side_effect = Exception("Connection failed")

        result = manager.healthy_connection

        assert result is False
        mock_logger.error.assert_called_once()
