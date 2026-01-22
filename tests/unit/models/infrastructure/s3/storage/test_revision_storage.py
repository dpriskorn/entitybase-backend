"""Unit tests for RevisionStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.storage.revision_storage import RevisionStorage


class TestRevisionStorage:
    """Unit tests for RevisionStorage class."""

    def test_store_revision_success(self) -> None:
        """Test successful revision storage."""
        storage = RevisionStorage()
        # Mock the connection manager to avoid S3 connection
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        storage.connection_manager = mock_connection_manager

        # Mock the store method
        with patch.object(storage, 'store', return_value=MagicMock(success=True)) as mock_store:
            # Mock RevisionData
            mock_revision_data = MagicMock()
            mock_revision_data.schema_version = "1.0.0"
            mock_revision_data.model_dump.return_value = {"entity": {"id": "Q42"}}
            mock_revision_data.created_at = "2023-01-01T12:00:00Z"

            result = storage.store_revision(12345, mock_revision_data)

            assert result.success is True
            mock_store.assert_called_once()
            args = mock_store.call_args
            assert args[0][0] == "12345"  # key is content_hash

    def test_store_revision_failure(self) -> None:
        """Test S3RevisionData storage failure."""
        storage = RevisionStorage()
        # Mock the connection manager to avoid S3 connection
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        storage.connection_manager = mock_connection_manager

        # Mock the store method to return failure
        with patch.object(storage, 'store', return_value=MagicMock(success=False)):
            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_revision(12345, revision_data)

            assert result.success is False

    def test_load_revision_success(self) -> None:
        """Test successful revision loading."""
        # Mock S3RevisionData
        mock_s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"entity": {"id": "Q42"}},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        storage = RevisionStorage()
        # Mock the connection manager to avoid S3 connection
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        storage.connection_manager = mock_connection_manager

        # Mock the load method
        with patch.object(storage, 'load', return_value=MagicMock(data=mock_s3_revision_data)):
            result = storage.load_revision(12345)

            # Should return S3RevisionData
            assert isinstance(result, S3RevisionData)
            assert result.revision == {"entity": {"id": "Q42"}}

    def test_load_revision_not_found(self) -> None:
        """Test loading non-existent revision."""
        storage = RevisionStorage()
        # Mock the connection manager to avoid S3 connection
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        storage.connection_manager = mock_connection_manager

        # Mock the load method to raise S3NotFoundError
        with patch.object(storage, 'load') as mock_load:
            mock_load.side_effect = S3NotFoundError("Revision not found")

            # The load_revision method should raise S3NotFoundError for missing data
            with pytest.raises(S3NotFoundError):
                storage.load_revision(12345)