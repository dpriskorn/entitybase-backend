"""Unit tests for LexemeStorage."""

from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.enums import MetadataType
from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage


class TestLexemeStorage:
    """Unit tests for LexemeStorage class."""

    def test_store_form_representation_success(self) -> None:
        """Test successful form representation storage."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        with patch.object(storage, 'store_metadata', return_value=MagicMock(success=True)) as mock_store_metadata:
            result = storage.store_form_representation("test text", 12345)

            assert result.success is True
            mock_store_metadata.assert_called_once_with(MetadataType.FORM_REPRESENTATIONS, 12345, "test text")

    def test_store_sense_gloss_success(self) -> None:
        """Test successful sense gloss storage."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        with patch.object(storage, 'store_metadata', return_value=MagicMock(success=True)) as mock_store_metadata:
            result = storage.store_sense_gloss("test gloss", 67890)

            assert result.success is True
            mock_store_metadata.assert_called_once_with(MetadataType.SENSE_GLOSSES, 67890, "test gloss")

    def test_load_form_representations_batch_success(self) -> None:
        """Test loading form representations batch."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        with patch.object(storage, 'load_metadata', side_effect=["text1", "text2"]) as mock_load_metadata:
            result = storage.load_form_representations_batch([123, 456])

            assert result == ["text1", "text2"]
            assert mock_load_metadata.call_count == 2
            mock_load_metadata.assert_any_call(MetadataType.FORM_REPRESENTATIONS, 123)
            mock_load_metadata.assert_any_call(MetadataType.FORM_REPRESENTATIONS, 456)

    def test_load_sense_glosses_batch_success(self) -> None:
        """Test loading sense glosses batch."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        with patch.object(storage, 'load_metadata', side_effect=["gloss1", "gloss2"]) as mock_load_metadata:
            result = storage.load_sense_glosses_batch([789, 101])

            assert result == ["gloss1", "gloss2"]
            assert mock_load_metadata.call_count == 2
            mock_load_metadata.assert_any_call(MetadataType.SENSE_GLOSSES, 789)
            mock_load_metadata.assert_any_call(MetadataType.SENSE_GLOSSES, 101)

    def test_load_form_representations_batch_with_errors(self) -> None:
        """Test loading form representations with some errors."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        with patch.object(storage, 'load_metadata', side_effect=["text1", Exception("not found"), "text3"]) as mock_load_metadata:
            result = storage.load_form_representations_batch([123, 456, 789])

            assert result == ["text1", None, "text3"]
            assert mock_load_metadata.call_count == 3

    def test_load_sense_glosses_batch_with_non_string_data(self) -> None:
        """Test loading sense glosses with non-string data."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        with patch('models.infrastructure.s3.storage.lexeme_storage.LexemeStorage.load_metadata', side_effect=["gloss1", {"invalid": "data"}, "gloss3"]) as mock_load_metadata:
            with patch('models.infrastructure.s3.storage.lexeme_storage.logger') as mock_logger:
                result = storage.load_sense_glosses_batch([111, 222, 333])

                assert result == ["gloss1", None, "gloss3"]
                mock_logger.warning.assert_called_once()

    def test_load_form_representations_batch_empty(self) -> None:
        """Test loading empty batch of form representations."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        result = storage.load_form_representations_batch([])

        assert result == []

    def test_load_sense_glosses_batch_empty(self) -> None:
        """Test loading empty batch of sense glosses."""
        mock_connection_manager = MagicMock()

        with patch('models.infrastructure.s3.storage.lexeme_storage.settings') as mock_settings:
            mock_settings.s3_terms_bucket = "test-terms"
            storage = LexemeStorage(connection_manager=mock_connection_manager)

        result = storage.load_sense_glosses_batch([])

        assert result == []