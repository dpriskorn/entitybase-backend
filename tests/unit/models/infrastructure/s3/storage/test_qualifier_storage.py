"""Unit tests for QualifierStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.storage.qualifier_storage import QualifierStorage


class TestQualifierStorage:
    """Unit tests for QualifierStorage class."""

    def test_store_qualifier_success(self) -> None:
        """Test successful qualifier storage."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)

        # Mock the store method
        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.store', return_value=MagicMock(success=True)) as mock_store:
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
            mock_store.assert_called_once()
            args, kwargs = mock_store.call_args
            assert args[0] == "12345"  # key
            assert args[1] == qualifier_data  # data
            assert kwargs["metadata"] == {"content_hash": "12345"}  # metadata

    def test_store_qualifier_failure(self) -> None:
        """Test qualifier storage failure."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.store', return_value=MagicMock(success=False)):
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
        data_dict = mock_qualifier_data.model_dump()

        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', return_value=MagicMock(data=data_dict)) as mock_load:
            result = storage.load_qualifier(12345)

            assert result == mock_qualifier_data
            mock_load.assert_called_once_with("12345")

    def test_load_qualifiers_batch_all_found(self) -> None:
        """Test batch loading when all qualifiers are found."""
        mock_qualifier_data1 = S3QualifierData(
            qualifier={"P580": []},
            content_hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )
        data_dict1 = mock_qualifier_data1.model_dump()
        mock_qualifier_data2 = S3QualifierData(
            qualifier={"P582": []},
            content_hash=67890,
            created_at="2023-01-02T12:00:00Z"
        )
        data_dict2 = mock_qualifier_data2.model_dump()

        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)

        # Mock load method to return different data for different keys
        def mock_load(key):
            if key == "12345":
                return MagicMock(data=data_dict1)
            elif key == "67890":
                return MagicMock(data=data_dict2)
            else:
                return None

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', side_effect=mock_load):
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
        data_dict = mock_qualifier_data.model_dump()

        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)

        # Mock load method to return data for first key, None for second
        def mock_load(key):
            if key == "12345":
                return MagicMock(data=data_dict)
            else:
                return None

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', side_effect=mock_load):
            result = storage.load_qualifiers_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] == mock_qualifier_data
            assert result[1] is None

    def test_load_qualifiers_batch_all_missing(self) -> None:
        """Test batch loading when all qualifiers are missing."""
        mock_connection_manager = MagicMock()
        storage = QualifierStorage(connection_manager=mock_connection_manager)
        storage.bucket = "test-qualifiers"

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', return_value=None):
            result = storage.load_qualifiers_batch([12345, 67890])

            assert len(result) == 2
            assert result[0] is None
            assert result[1] is None

    def test_load_qualifiers_batch_empty_list(self) -> None:
        """Test batch loading with empty hash list."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)
        result = storage.load_qualifiers_batch([])

        assert result == []

    def test_load_qualifier_not_found(self) -> None:
        """Test loading qualifier when not found."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.qualifier_storage.settings') as mock_settings:
            mock_settings.s3_qualifiers_bucket = "test-qualifiers"
            storage = QualifierStorage(connection_manager=mock_connection_manager)

        with patch('models.infrastructure.s3.base_storage.BaseS3Storage.load', return_value=None) as mock_load:
            with pytest.raises(S3NotFoundError, match="Qualifier not found: 999"):
                storage.load_qualifier(999)