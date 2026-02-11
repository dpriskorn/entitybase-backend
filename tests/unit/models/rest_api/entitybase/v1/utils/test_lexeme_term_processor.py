"""Unit tests for lexeme term processor."""

from unittest.mock import MagicMock

from models.rest_api.entitybase.v1.utils.lexeme_term_processor import (
    process_lexeme_terms,
    _process_term_data,
    TermProcessingConfig,
)


class TestProcessLexemeTerms:
    """Unit tests for lexeme term processing."""

    def test_process_lexeme_terms_no_data(self) -> None:
        """Test processing with no forms or senses."""
        mock_s3 = MagicMock()

        process_lexeme_terms([], [], mock_s3)

        mock_s3.store_form_representation.assert_not_called()
        mock_s3.store_sense_gloss.assert_not_called()

    def test_process_lexeme_terms_with_forms(self) -> None:
        """Test processing lexeme forms."""
        mock_s3 = MagicMock()
        mock_s3.store_form_representation = MagicMock()

        forms = [
            {
                "id": "L123-F1",
                "representations": {"en": {"value": "cats"}},
            }
        ]

        process_lexeme_terms(forms, [], mock_s3)

        mock_s3.store_form_representation.assert_called_once()

    def test_process_lexeme_terms_with_senses(self) -> None:
        """Test processing lexeme senses."""
        mock_s3 = MagicMock()
        mock_s3.store_sense_gloss = MagicMock()

        senses = [
            {
                "id": "L123-S1",
                "glosses": {"en": {"value": "feline animal"}},
            }
        ]

        process_lexeme_terms([], senses, mock_s3)

        mock_s3.store_sense_gloss.assert_called_once()

    def test_process_lexeme_terms_calls_callbacks(self) -> None:
        """Test that callbacks are invoked for each stored hash."""
        mock_s3 = MagicMock()
        mock_s3.store_form_representation = MagicMock()
        mock_s3.store_sense_gloss = MagicMock()

        form_callback_calls = []
        gloss_callback_calls = []

        forms = [{"id": "L123-F1", "representations": {"en": {"value": "cats"}}}]
        senses = [{"id": "L123-S1", "glosses": {"en": {"value": "animal"}}}]

        def form_callback(hash_val):
            form_callback_calls.append(hash_val)

        def gloss_callback(hash_val):
            gloss_callback_calls.append(hash_val)

        process_lexeme_terms(forms, senses, mock_s3, form_callback, gloss_callback)

        assert len(form_callback_calls) == 1
        assert len(gloss_callback_calls) == 1

    def test_process_lexeme_terms_handles_s3_errors(self) -> None:
        """Test that S3 storage errors are logged but don't halt processing."""
        mock_s3 = MagicMock()
        mock_s3.store_form_representation.side_effect = Exception("S3 error")
        mock_s3.store_sense_gloss.side_effect = Exception("S3 error")

        forms = [{"id": "L123-F1", "representations": {"en": {"value": "cats"}}}]
        senses = [{"id": "L123-S1", "glosses": {"en": {"value": "animal"}}}]

        # Should not raise exception
        process_lexeme_terms(forms, senses, mock_s3)

        assert True  # No exception raised

    def test_process_term_data_success(self) -> None:
        """Test processing term data successfully."""
        mock_s3 = MagicMock()
        mock_s3.store_form_representation = MagicMock()

        terms = [
            {"representations": {"en": {"value": "cats"}, "de": {"value": "Katzen"}}}
        ]

        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )

        _process_term_data(terms, mock_s3, config)

        assert mock_s3.store_form_representation.call_count == 2

    def test_process_term_data_missing_data_key(self) -> None:
        """Test processing term data when data key is missing."""
        mock_s3 = MagicMock()

        terms = [
            {"id": "L123-F1"}  # Missing representations
        ]

        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )

        _process_term_data(terms, mock_s3, config)

        mock_s3.store_form_representation.assert_not_called()

    def test_process_term_data_missing_value(self) -> None:
        """Test processing term data when value is missing."""
        mock_s3 = MagicMock()

        terms = [
            {"representations": {"en": {}}}  # Missing value
        ]

        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )

        _process_term_data(terms, mock_s3, config)

        mock_s3.store_form_representation.assert_not_called()

    def test_process_term_data_initializes_hash_key(self) -> None:
        """Test that hash_key dict is initialized if missing."""
        mock_s3 = MagicMock()
        mock_s3.store_form_representation = MagicMock()

        terms = [{"representations": {"en": {"value": "cats"}}}]

        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )

        _process_term_data(terms, mock_s3, config)

        # Check that hash_key was added to term
        assert "representation_hashes" in terms[0]
