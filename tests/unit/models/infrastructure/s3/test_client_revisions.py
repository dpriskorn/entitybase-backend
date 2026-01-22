"""Unit tests for S3 client revision methods."""

from unittest.mock import MagicMock, patch

from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.s3.revision.s3_revision_data import S3RevisionData


class TestS3ClientRevisions:
    """Unit tests for S3 client revision methods."""

    def test_store_revision_success(self) -> None:
        """Test successful revision storage via S3 client."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            client = MyS3Client()

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

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            client = MyS3Client()

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

    def test_revision_storage_lazy_initialization(self) -> None:
        """Test that RevisionStorage is created on demand."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            with patch("models.infrastructure.s3.storage.revision_storage.RevisionStorage") as mock_storage_class:
                mock_storage = MagicMock()
                mock_storage_class.return_value = mock_storage
                mock_storage.store_revision.return_value = MagicMock(success=True)

                client = MyS3Client()

                # Initially revisions should be None
                assert client.revisions is None

                # Call store_revision to trigger lazy initialization
                revision_data = S3RevisionData(
                    schema="1.0.0",
                    revision={"entity": {"id": "Q42"}},
                    hash=12345,
                    created_at="2023-01-01T12:00:00Z"
                )

                client.store_revision(12345, revision_data)

                # Verify RevisionStorage was created
                mock_storage_class.assert_called_once()
                assert client.revisions == mock_storage