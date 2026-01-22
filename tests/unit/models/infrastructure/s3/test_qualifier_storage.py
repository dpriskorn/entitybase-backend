"""Unit tests for QualifierStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.revision.s3_qualifier_data import S3QualifierData
from models.infrastructure.s3.storage.qualifier_storage import QualifierStorage


class TestQualifierStorage:
    """Unit tests for QualifierStorage class."""

    def test_store_qualifier_success(self) -> None:
        """Test successful qualifier storage."""
        # Mock the base storage
        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=True)

            storage = QualifierStorage()
            qualifier_data = S3QualifierData(
                qualifier={
                    "P580": [
                        {
                            "snaktype": "value",
                            "property": "P580",
                            "datatype": "time",
                            "datavalue": {
                                "value": {
                                    "time": "+2023-01-01T00:00:00Z",
                                    "timezone": 0,
                                    "before": 0,
                                    "after": 0,
                                    "precision": 11,
                                    "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                                },
                                "type": "time",
                            },
                        }
                    ]
                },
                content_hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_qualifier(12345, qualifier_data)

            assert result.success is True
            mock_instance.store.assert_called_once()
            args = mock_instance.store.call_args
            assert args[0][0] == "12345"  # key
            assert args[0][1] == qualifier_data  # data
            assert args[0][2] == {"content_hash": "12345"}  # metadata

    def test_store_qualifier_failure(self) -> None:
        """Test qualifier storage failure."""
        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.store.return_value = MagicMock(success=False)

            storage = QualifierStorage()
            qualifier_data = S3QualifierData(
                qualifier={"P580": []},
                content_hash=12345,
                created_at="2023-01-01T12:00:00Z"
            )

            result = storage.store_qualifier(12345, qualifier_data)

            assert result.success is False

    def test_load_qualifier_success(self) -> None:
        """Test successful qualifier loading."""
        mock_qualifier_data = S3QualifierData(
            qualifier={"P580": []},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.return_value = MagicMock(data=mock_qualifier_data)

            storage = QualifierStorage()
            result = storage.load_qualifier(12345)

            assert result == mock_qualifier_data
            mock_instance.load.assert_called_once_with("12345")

    def test_load_qualifier_not_found(self) -> None:
        """Test loading non-existent qualifier."""
        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.side_effect = S3NotFoundError("Qualifier not found")

            storage = QualifierStorage()

            with pytest.raises(S3NotFoundError):
                storage.load_qualifier(12345)

    def test_load_qualifiers_batch_all_found(self) -> None:
        """Test batch loading when all qualifiers are found."""
        mock_qualifier_data1 = S3QualifierData(
            qualifier={"P580": []},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )
        mock_qualifier_data2 = S3QualifierData(
            qualifier={"P582": []},
            content_hash=67890,
            created_at="2023-01-02T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance

            # Mock load method to return different data for different keys
            def mock_load(key):
                if key == "12345":
                    return MagicMock(data=mock_qualifier_data1)
                elif key == "67890":
                    return MagicMock(data=mock_qualifier_data2)
                else:
                    raise S3NotFoundError("Not found")

            mock_instance.load.side_effect = mock_load

            storage = QualifierStorage()
            result = storage.load_qualifiers_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_qualifier_data1
            assert result[1] == mock_qualifier_data2

    def test_load_qualifiers_batch_some_missing(self) -> None:
        """Test batch loading when some qualifiers are missing."""
        mock_qualifier_data = S3QualifierData(
            qualifier={"P580": []},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance

            # Mock load method to return data for first key, raise exception for second
            def mock_load(key):
                if key == "12345":
                    return MagicMock(data=mock_qualifier_data)
                else:
                    raise S3NotFoundError("Not found")

            mock_instance.load.side_effect = mock_load

            storage = QualifierStorage()
            result = storage.load_qualifiers_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_qualifier_data
            assert result[1] is None

    def test_load_qualifiers_batch_all_missing(self) -> None:
        """Test batch loading when all qualifiers are missing."""
        with patch("models.infrastructure.s3.storage.qualifier_storage.BaseS3Storage") as mock_base:
            mock_instance = MagicMock()
            mock_base.return_value = mock_instance
            mock_instance.load.side_effect = S3NotFoundError("Not found")

            storage = QualifierStorage()
            result = storage.load_qualifiers_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] is None
            assert result[1] is None

    def test_load_qualifiers_batch_empty_list(self) -> None:
        """Test batch loading with empty hash list."""
        storage = QualifierStorage()
        result = storage.load_qualifiers_batch([])

        assert result == []