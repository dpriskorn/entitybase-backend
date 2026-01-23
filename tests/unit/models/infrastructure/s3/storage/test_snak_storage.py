"""Unit tests for SnakStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.snak_data import S3SnakData
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.storage.snak_storage import SnakStorage


class TestSnakStorage:
    """Unit tests for SnakStorage class."""

    def test_store_snak_success(self) -> None:
        """Test successful snak storage."""
        # Mock the base storage
        with patch("models.infrastructure.s3.storage.snak_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=True)

            storage = SnakStorage()
            snak_data = S3SnakData(
                schema_version="1.0.0",
                snak={
                    "snaktype": "value",
                    "property": "P31",
                    "datatype": "wikibase-item",
                    "datavalue": {"value": {"id": "Q5"}, "type": "wikibase-entityid"}
                },
                content_hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_snak(12345, snak_data)

            assert result.success is True
            mock_instance.store.assert_called_once()
            args = mock_instance.store.call_args
            assert args[0][0] == "12345"  # key
            assert args[0][1] == snak_data  # data
            assert args[0][2] == {"content_hash": "12345"}  # metadata

    def test_store_snak_failure(self) -> None:
        """Test snak storage failure."""
        with patch("models.infrastructure.s3.storage.snak_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=False)

            mock_connection_manager = MagicMock()
            storage = SnakStorage(connection_manager=mock_connection_manager)
            snak_data = S3SnakData(
                schema_version="1.0.0",
                snak={"snaktype": "value", "property": "P31"},
                content_hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_snak(12345, snak_data)

            assert result.success is False

    def test_load_snak_success(self) -> None:
        """Test successful snak loading."""
        mock_snak_data = S3SnakData(
            schema_version="1.0.0",
            snak={"snaktype": "value", "property": "P31"},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.snak_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.return_value = MagicMock(data=mock_snak_data)

            mock_connection_manager = MagicMock()
            storage = SnakStorage(connection_manager=mock_connection_manager)
            result = storage.load_snak(12345)

            assert result == mock_snak_data
            mock_instance.load.assert_called_once_with("12345")

    def test_load_snak_not_found(self) -> None:
        """Test loading non-existent snak."""
        with patch("models.infrastructure.s3.storage.snak_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.side_effect = S3NotFoundError("Snak not found")

            mock_connection_manager = MagicMock()
            storage = SnakStorage(connection_manager=mock_connection_manager)

            with pytest.raises(S3NotFoundError):
                storage.load_snak(12345)

    def test_load_snaks_batch_all_found(self) -> None:
        """Test batch loading when all snaks are found."""
        mock_snak_data1 = S3SnakData(
            schema_version="1.0.0",
            snak={"snaktype": "value", "property": "P31"},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )
        mock_snak_data2 = S3SnakData(
            schema_version="1.0.0",
            snak={"snaktype": "somevalue", "property": "P32"},
            content_hash=67890,
            created_at="2023-01-02T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.snak_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance

            # Mock load method to return different data for different keys
            def mock_load(key):
                if key == "12345":
                    return MagicMock(data=mock_snak_data1)
                elif key == "67890":
                    return MagicMock(data=mock_snak_data2)
                else:
                    raise S3NotFoundError("Not found")

            mock_instance.load.side_effect = mock_load

            mock_connection_manager = MagicMock()
            storage = SnakStorage(connection_manager=mock_connection_manager)
            result = storage.load_snaks_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_snak_data1
            assert result[1] == mock_snak_data2

    def test_load_snaks_batch_some_missing(self) -> None:
        """Test batch loading when some snaks are missing."""
        mock_snak_data = S3SnakData(
            schema_version="1.0.0",
            snak={"snaktype": "value", "property": "P31"},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_connection_manager = MagicMock()
        storage = SnakStorage(connection_manager=mock_connection_manager)

        # Mock load method to return data for first key, raise exception for second
        def mock_load(key):
            if key == "12345":
                return MagicMock(data=mock_snak_data)
            else:
                raise S3NotFoundError("Not found")

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', side_effect=mock_load):
            result = storage.load_snaks_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_snak_data
            assert result[1] is None

    def test_load_snaks_batch_all_missing(self) -> None:
        """Test batch loading when all snaks are missing."""
        mock_connection_manager = MagicMock()
        storage = SnakStorage(connection_manager=mock_connection_manager)

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', side_effect=S3NotFoundError("Not found")):
            result = storage.load_snaks_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] is None
            assert result[1] is None

    def test_load_snaks_batch_empty_list(self) -> None:
        """Test batch loading with empty hash list."""
        mock_connection_manager = MagicMock()
        storage = SnakStorage(connection_manager=mock_connection_manager)
        result = storage.load_snaks_batch([])

        assert result == []