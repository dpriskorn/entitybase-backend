"""Unit tests for RevisionStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.revision.s3_revision_data import S3RevisionData
from models.infrastructure.s3.storage.revision_storage import RevisionStorage


class TestRevisionStorage:
    """Unit tests for RevisionStorage class."""

    def test_store_revision_success(self) -> None:
        """Test successful S3RevisionData storage."""
        # Mock the base storage
        with patch("models.infrastructure.s3.storage.revision_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=True)

            storage = RevisionStorage()
            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_revision(12345, revision_data)

            assert result.success is True
            mock_instance.store.assert_called_once()
            args = mock_instance.store.call_args
            assert args[0][0] == "12345"  # key
            assert args[0][1] == revision_data  # data
            assert args[0][2] == {"content_hash": "12345"}  # metadata

    def test_store_revision_failure(self) -> None:
        """Test S3RevisionData storage failure."""
        with patch("models.infrastructure.s3.storage.revision_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=False)

            storage = RevisionStorage()
            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_revision(12345, revision_data)

            assert result.success is False

    def test_load_revision_success(self) -> None:
        """Test successful S3RevisionData loading."""
        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"entity": {"id": "Q42"}},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.revision_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.return_value = MagicMock(data=mock_revision_data)

            storage = RevisionStorage()
            result = storage.load_revision(12345)

            assert result == mock_revision_data
            mock_instance.load.assert_called_once_with("12345")

    def test_load_revision_not_found(self) -> None:
        """Test loading non-existent revision."""
        with patch("models.infrastructure.s3.storage.revision_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.side_effect = S3NotFoundError("Revision not found")

            storage = RevisionStorage()

            with pytest.raises(S3NotFoundError):
                storage.load_revision(12345)

    def test_load_revision_wrong_type(self) -> None:
        """Test loading revision with wrong data type."""
        with patch("models.infrastructure.s3.storage.revision_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.return_value = MagicMock(data="not a revision")  # Wrong type

            storage = RevisionStorage()

            with pytest.raises(AssertionError):
                storage.load_revision(12345)