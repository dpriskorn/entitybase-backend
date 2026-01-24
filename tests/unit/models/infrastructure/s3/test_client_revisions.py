"""Unit tests for S3 client revision methods."""

from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.data.config.s3 import S3Config
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientRevisions:
    """Unit tests for S3 client revision methods."""

    def test_store_revision_success(self) -> None:
        """Test successful revision storage via S3 client."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1"
        )

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            client = MyS3Client(config=config)

            # Mock the revision storage
            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage
            mock_revision_storage.store_revision.return_value = MagicMock(success=True)

            # Test data
            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            # Call the method
            client.store_revision(12345, revision_data)

            # Verify the storage was called
            mock_revision_storage.store_revision.assert_called_once_with(12345, revision_data)

    def test_load_revision_success(self) -> None:
        """Test successful revision loading via S3 client."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1"
        )

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            client = MyS3Client(config=config)

            # Mock the revision storage
            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage

            expected_revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )
            mock_revision_storage.load_revision.return_value = expected_revision_data

            # Call the method
            result = client.load_revision(12345)

            # Verify the result
            assert result == expected_revision_data
            mock_revision_storage.load_revision.assert_called_once_with(12345)

