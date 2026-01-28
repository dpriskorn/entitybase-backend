"""Unit tests for S3 client revision methods."""

import pytest
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

    def test_read_revision_with_content_hash(self):
        """Test read_revision queries content_hash and loads from S3."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1"
        )

        # Mock vitess client and id_resolver
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            # Mock revision repository
            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = 12345678901234567890

            # Mock revision storage
            mock_revision_storage = MagicMock()
            expected_revision_data = {"entity": {"id": "Q42"}}
            mock_revision_storage.load_revision.return_value = expected_revision_data
            client.revisions = mock_revision_storage

            # Call read_revision
            with patch("models.infrastructure.s3.client.RevisionRepository", return_value=mock_revision_repo):
                result = client.read_revision("Q42", 1)

            # Verify
            assert result == expected_revision_data
            mock_id_resolver.resolve_id.assert_called_once_with("Q42")
            mock_revision_repo.get_content_hash.assert_called_once_with(123, 1)
            mock_revision_storage.load_revision.assert_called_once_with(12345678901234567890)

    def test_read_revision_entity_not_found(self):
        """Test read_revision raises 404 when entity not found."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1"
        )

        # Mock vitess client with entity not found
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch("models.infrastructure.s3.client.S3ConnectionManager", return_value=mock_connection_manager):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            # Call read_revision and expect error
            with pytest.raises(Exception):
                client.read_revision("Q999", 1)

