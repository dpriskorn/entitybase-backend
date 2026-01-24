"""Unit tests for LexemeStorage."""

from unittest.mock import MagicMock, patch

from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage


class TestLexemeStorage:
    """Unit tests for LexemeStorage class."""



    

    

    

    

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