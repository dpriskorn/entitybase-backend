"""Unit tests for ReferenceStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.storage.reference_storage import ReferenceStorage


class TestReferenceStorage:
    """Unit tests for ReferenceStorage class."""

    def test_store_reference_success(self) -> None:
        """Test successful reference storage."""
        # Mock the base storage
        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=True)

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)
            reference_data = S3ReferenceData(
                reference={
                    "snaks": {
                        "P854": [
                            {
                                "snaktype": "value",
                                "property": "P854",
                                "datatype": "url",
                                "datavalue": {
                                    "value": "https://example.com",
                                    "type": "string",
                                },
                            }
                        ]
                    },
                    "snaks-order": ["P854"]
                },
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_reference(12345, reference_data)

            assert result.success is True
            mock_instance.store.assert_called_once()
            args = mock_instance.store.call_args
            assert args[0][0] == "12345"  # key
            assert args[0][1] == reference_data  # data
            assert args[0][2] == {"content_hash": "12345"}  # metadata

    def test_store_reference_failure(self) -> None:
        """Test reference storage failure."""
        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=False)

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)
            reference_data = S3ReferenceData(
                reference={"snaks": {}, "snaks-order": []},
                hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_reference(12345, reference_data)

            assert result.success is False

    def test_load_reference_success(self) -> None:
        """Test successful reference loading."""
        mock_reference_data = S3ReferenceData(
            reference={"snaks": {}, "snaks-order": []},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.return_value = MagicMock(data=mock_reference_data)

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)
            result = storage.load_reference(12345)

            assert result == mock_reference_data
            mock_instance.load.assert_called_once_with("12345")

    def test_load_reference_not_found(self) -> None:
        """Test loading non-existent reference."""
        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.side_effect = S3NotFoundError("Reference not found")

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)

            with pytest.raises(S3NotFoundError):
                storage.load_reference(12345)

    def test_load_references_batch_all_found(self) -> None:
        """Test batch loading when all references are found."""
        mock_reference_data1 = S3ReferenceData(
            reference={"snaks": {"P854": []}, "snaks-order": ["P854"]},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )
        mock_reference_data2 = S3ReferenceData(
            reference={"snaks": {"P248": []}, "snaks-order": ["P248"]},
            hash=67890,
            created_at="2023-01-02T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance

            # Mock load method to return different data for different keys
            def mock_load(key):
                if key == "12345":
                    return MagicMock(data=mock_reference_data1)
                elif key == "67890":
                    return MagicMock(data=mock_reference_data2)
                else:
                    raise S3NotFoundError("Not found")

            mock_instance.load.side_effect = mock_load

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)
            result = storage.load_references_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_reference_data1
            assert result[1] == mock_reference_data2

    def test_load_references_batch_some_missing(self) -> None:
        """Test batch loading when some references are missing."""
        mock_reference_data = S3ReferenceData(
            reference={"snaks": {"P854": []}, "snaks-order": ["P854"]},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance

            # Mock load method to return data for first key, raise exception for second
            def mock_load(key):
                if key == "12345":
                    return MagicMock(data=mock_reference_data)
                else:
                    raise S3NotFoundError("Not found")

            mock_instance.load.side_effect = mock_load

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)
            result = storage.load_references_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_reference_data
            assert result[1] is None

    def test_load_references_batch_all_missing(self) -> None:
        """Test batch loading when all references are missing."""
        with patch("models.infrastructure.s3.storage.reference_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.side_effect = S3NotFoundError("Not found")

            mock_connection_manager = MagicMock()
            storage = ReferenceStorage(connection_manager=mock_connection_manager)
            result = storage.load_references_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] is None
            assert result[1] is None

    def test_load_references_batch_empty_list(self) -> None:
        """Test batch loading with empty hash list."""
        mock_connection_manager = MagicMock()
        storage = ReferenceStorage(connection_manager=mock_connection_manager)
        result = storage.load_references_batch([])

        assert result == []