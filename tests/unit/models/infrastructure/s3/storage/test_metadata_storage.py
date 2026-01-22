"""Unit tests for MetadataStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.enums import MetadataType
from models.infrastructure.s3.storage.metadata_storage import MetadataStorage
from models.rest_api.utils import ValidationError


class TestMetadataStorage:
    """Unit tests for MetadataStorage class."""

    def test_get_bucket_for_type_terms(self) -> None:
        """Test getting bucket for term types."""
        with patch('models.infrastructure.s3.storage.metadata_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            mock_settings.s3_sitelinks_bucket = "test-sitelinks"

            assert MetadataStorage._get_bucket_for_type(MetadataType.LABELS) == "test-terms"
            assert MetadataStorage._get_bucket_for_type(MetadataType.DESCRIPTIONS) == "test-terms"
            assert MetadataStorage._get_bucket_for_type(MetadataType.ALIASES) == "test-terms"
            assert MetadataStorage._get_bucket_for_type(MetadataType.FORM_REPRESENTATIONS) == "test-terms"
            assert MetadataStorage._get_bucket_for_type(MetadataType.SENSE_GLOSSES) == "test-terms"

    def test_get_bucket_for_type_sitelinks(self) -> None:
        """Test getting bucket for sitelinks."""
        with patch('models.infrastructure.s3.storage.metadata_storage.settings') as mock_settings:
            mock_settings.s3_sitelinks_bucket = "test-sitelinks"

            assert MetadataStorage._get_bucket_for_type(MetadataType.SITELINKS) == "test-sitelinks"

    def test_get_bucket_for_type_unknown(self) -> None:
        """Test getting bucket for unknown type raises error."""
        with pytest.raises(ValidationError):
            MetadataStorage._get_bucket_for_type("unknown")  # type: ignore

    def test_store_metadata_success(self) -> None:
        """Test successful metadata storage."""
        mock_connection_manager = MagicMock()

        storage = MetadataStorage(connection_manager=mock_connection_manager)
        storage.bucket = "original-bucket"

        with patch.object(storage, 'store', return_value=MagicMock(success=True)) as mock_store:
            with patch('models.infrastructure.s3.storage.metadata_storage.settings') as mock_settings:
                mock_settings.s3_terms_bucket = "test-terms"

                result = storage.store_metadata(MetadataType.LABELS, 12345, "test label")

                assert result.success is True
                mock_store.assert_called_once_with("12345", "test label", content_type="text/plain")
                assert storage.bucket == "original-bucket"  # restored

    def test_load_metadata_success(self) -> None:
        """Test successful metadata loading."""
        mock_connection_manager = MagicMock()
        mock_load_result = MagicMock()
        mock_load_result.data = "loaded data"

        storage = MetadataStorage(connection_manager=mock_connection_manager)
        storage.bucket = "original-bucket"

        with patch.object(storage, 'load', return_value=mock_load_result) as mock_load:
            with patch('models.infrastructure.s3.storage.metadata_storage.settings') as mock_settings:
                mock_settings.s3_sitelinks_bucket = "test-sitelinks"

                result = storage.load_metadata(MetadataType.SITELINKS, 67890)

                assert result == "loaded data"
                mock_load.assert_called_once_with("67890")
                assert storage.bucket == "original-bucket"  # restored

    def test_load_metadata_not_found(self) -> None:
        """Test loading metadata when not found."""
        mock_connection_manager = MagicMock()

        storage = MetadataStorage(connection_manager=mock_connection_manager)

        with patch.object(storage, 'load', return_value=None) as mock_load:
            with patch('models.infrastructure.s3.storage.metadata_storage.settings') as mock_settings:
                mock_settings.s3_terms_bucket = "test-terms"

                result = storage.load_metadata(MetadataType.LABELS, 11111)

                assert result is None
                mock_load.assert_called_once_with("11111")

    def test_delete_metadata_success(self) -> None:
        """Test successful metadata deletion."""
        mock_connection_manager = MagicMock()

        storage = MetadataStorage(connection_manager=mock_connection_manager)
        storage.bucket = "original-bucket"

        with patch.object(storage, 'delete', return_value=MagicMock(success=True)) as mock_delete:
            with patch('models.infrastructure.s3.storage.metadata_storage.settings') as mock_settings:
                mock_settings.s3_terms_bucket = "test-terms"

                result = storage.delete_metadata(MetadataType.ALIASES, 22222)

                assert result.success is True
                mock_delete.assert_called_once_with("22222")
                assert storage.bucket == "original-bucket"  # restored
