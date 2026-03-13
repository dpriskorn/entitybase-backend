"""Unit tests for S3 client disconnect."""

from unittest.mock import MagicMock, patch

from models.data.config.s3 import S3Config
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientDisconnect:
    """Unit tests for S3 client disconnect."""

    def test_disconnect(self):
        """Test disconnect clears connection."""
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
            mock_connection_manager.boto_client = "some_client"

            client.disconnect()

            assert mock_connection_manager.boto_client is None
