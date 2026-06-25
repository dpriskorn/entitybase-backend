"""Unit tests for lexeme_term_processor."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.utils.lexeme_term_processor import (
    LexemeTermProcessorConfig,
    TermProcessingConfig,
    process_lexeme_terms,
    _process_lexeme_lemmas,
    _process_term_data,
)


class TestTermProcessingConfig:
    """Unit tests for TermProcessingConfig."""

    def test_term_processing_config_creation(self):
        """Test creating TermProcessingConfig with all fields."""
        config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )
        assert config.data_key == "value"
        assert config.hash_key == "lemma_hashes"
        assert config.storage_method == "store_lemma"
        assert config.term_type == "lemma"

    def test_term_processing_config_extra_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            TermProcessingConfig(
                data_key="value",
                hash_key="lemma_hashes",
                storage_method="store_lemma",
                term_type="lemma",
                extra_field="not allowed",
            )


class TestLexemeTermProcessorConfig:
    """Unit tests for LexemeTermProcessorConfig."""

    def test_lexeme_term_processor_config_minimal(self):
        """Test creating config with only required fields."""
        s3_client = MagicMock()
        config = LexemeTermProcessorConfig(s3_client=s3_client)
        assert config.s3_client == s3_client
        assert config.lemmas is None
        assert config.on_form_stored is None
        assert config.on_gloss_stored is None
        assert config.on_lemma_stored is None

    def test_lexeme_term_processor_config_full(self):
        """Test creating config with all fields including callbacks."""
        s3_client = MagicMock()
        on_form_stored = MagicMock()
        on_gloss_stored = MagicMock()
        on_lemma_stored = MagicMock()
        lemmas = {"en": {"value": "test"}}

        config = LexemeTermProcessorConfig(
            s3_client=s3_client,
            lemmas=lemmas,
            on_form_stored=on_form_stored,
            on_gloss_stored=on_gloss_stored,
            on_lemma_stored=on_lemma_stored,
        )

        assert config.s3_client == s3_client
        assert config.lemmas == lemmas
        assert config.on_form_stored == on_form_stored
        assert config.on_gloss_stored == on_gloss_stored
        assert config.on_lemma_stored == on_lemma_stored


class TestProcessLexemeTerms:
    """Unit tests for process_lexeme_terms function."""

    def test_process_lexeme_terms_empty_all(self):
        """Test processing with empty forms, senses, and no lemmas."""
        s3_client = MagicMock()
        config = LexemeTermProcessorConfig(s3_client=s3_client)

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.logger"
        ) as mock_logger:
            process_lexeme_terms([], [], config)

            mock_logger.debug.assert_any_call(
                f"Processing lexeme terms: 0 forms, 0 senses, 0 lemmas"
            )
            mock_logger.debug.assert_any_call("No forms, senses, or lemmas to process")

    def test_process_lexeme_terms_with_forms(self):
        """Test processing with forms only (also calls _process_term_data for empty senses)."""
        s3_client = MagicMock()
        config = LexemeTermProcessorConfig(s3_client=s3_client)

        forms = [{"representations": {"en": {"value": "test"}}}]

        with (
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor._process_term_data"
            ) as mock_process_data,
            patch("models.rest_api.entitybase.v1.utils.lexeme_term_processor.logger"),
        ):
            mock_process_data.return_value = None

            process_lexeme_terms(forms, [], config)

            assert mock_process_data.call_count == 2

    def test_process_lexeme_terms_with_senses(self):
        """Test processing with senses only (also calls _process_term_data for empty forms)."""
        s3_client = MagicMock()
        config = LexemeTermProcessorConfig(s3_client=s3_client)

        senses = [{"glosses": {"en": {"value": "test gloss"}}}]

        with (
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor._process_term_data"
            ) as mock_process_data,
            patch("models.rest_api.entitybase.v1.utils.lexeme_term_processor.logger"),
        ):
            mock_process_data.return_value = None

            process_lexeme_terms([], senses, config)

            assert mock_process_data.call_count == 2

    def test_process_lexeme_terms_with_lemmas(self):
        """Test processing with lemmas."""
        s3_client = MagicMock()
        lemmas = {"en": {"value": "test lemma"}}
        config = LexemeTermProcessorConfig(s3_client=s3_client, lemmas=lemmas)

        with (
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor._process_lexeme_lemmas"
            ) as mock_process_lemmas,
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor._process_term_data"
            ) as mock_process_data,
            patch("models.rest_api.entitybase.v1.utils.lexeme_term_processor.logger"),
        ):
            mock_process_lemmas.return_value = None
            mock_process_data.return_value = None

            process_lexeme_terms([], [], config)

            mock_process_lemmas.assert_called_once()


class TestProcessLexemeLemmas:
    """Unit tests for _process_lexeme_lemmas function."""

    def test_process_lexeme_lemmas_basic(self):
        """Test basic lemma processing."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )
        lemmas = {"en": {"value": "test lemma"}}

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_lexeme_lemmas(lemmas, s3_client, config, None)

            assert "lemma_hashes" in lemmas
            assert "en" in lemmas["lemma_hashes"]
            assert lemmas["lemma_hashes"]["en"] == 12345
            s3_client.store_lemma.assert_called_once_with("test lemma", 12345)

    def test_process_lexeme_lemmas_with_callback(self):
        """Test lemma processing with callback."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )
        lemmas = {"en": {"value": "test lemma"}}
        callback = MagicMock()

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_lexeme_lemmas(lemmas, s3_client, config, callback)

            callback.assert_called_once_with(12345)

    def test_process_lexeme_lemmas_skips_existing_hash_key(self):
        """Test that lemma processing skips lemma_hashes key itself."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )
        lemmas = {
            "en": {"value": "test lemma"},
            "lemma_hashes": {"already": 999},
        }

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_lexeme_lemmas(lemmas, s3_client, config, None)

            assert lemmas["lemma_hashes"]["en"] == 12345
            assert lemmas["lemma_hashes"]["already"] == 999

    def test_process_lexeme_lemmas_skips_missing_value(self):
        """Test that lemma processing skips entries without value key."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )
        lemmas = {"en": {"language": "en"}}

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor_class.return_value = mock_extractor

            _process_lexeme_lemmas(lemmas, s3_client, config, None)

            assert "en" not in lemmas.get("lemma_hashes", {})

    def test_process_lexeme_lemmas_handles_storage_exception(self):
        """Test that lemma processing handles S3 storage exceptions gracefully."""
        s3_client = MagicMock()
        s3_client.store_lemma.side_effect = Exception("S3 Error")

        config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )
        lemmas = {"en": {"value": "test lemma"}}

        with (
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
            ) as mock_extractor_class,
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor.logger"
            ) as mock_logger,
        ):
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_lexeme_lemmas(lemmas, s3_client, config, None)

            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Failed to store lemma" in call_args


class TestProcessTermData:
    """Unit tests for _process_term_data function."""

    def test_process_term_data_basic(self):
        """Test basic term data processing."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )
        terms = [{"representations": {"en": {"value": "test form"}}}]

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_term_data(terms, s3_client, config, None)

            assert "representation_hashes" in terms[0]
            assert "en" in terms[0]["representation_hashes"]
            s3_client.store_form_representation.assert_called_once_with(
                "test form", 12345
            )

    def test_process_term_data_with_callback(self):
        """Test term data processing with callback."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="glosses",
            hash_key="gloss_hashes",
            storage_method="store_sense_gloss",
            term_type="sense gloss",
        )
        terms = [{"glosses": {"en": {"value": "test gloss"}}}]
        callback = MagicMock()

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_term_data(terms, s3_client, config, callback)

            callback.assert_called_once_with(12345)

    def test_process_term_data_skips_missing_data_key(self):
        """Test that term data processing skips entries without data key."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )
        terms = [{"other_key": "value"}]

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor_class.return_value = mock_extractor

            _process_term_data(terms, s3_client, config, None)

            assert "representation_hashes" not in terms[0]

    def test_process_term_data_skips_missing_value_in_lang(self):
        """Test that term data processing skips language entries without value."""
        s3_client = MagicMock()
        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )
        terms = [{"representations": {"en": {"language": "en"}}}]

        with patch(
            "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
        ) as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor_class.return_value = mock_extractor

            _process_term_data(terms, s3_client, config, None)

            assert "en" not in terms[0].get("representation_hashes", {})

    def test_process_term_data_handles_storage_exception(self):
        """Test that term data processing handles S3 storage exceptions gracefully."""
        s3_client = MagicMock()
        s3_client.store_form_representation.side_effect = Exception("S3 Error")

        config = TermProcessingConfig(
            data_key="representations",
            hash_key="representation_hashes",
            storage_method="store_form_representation",
            term_type="form representation",
        )
        terms = [{"representations": {"en": {"value": "test form"}}}]

        with (
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor.MetadataExtractor"
            ) as mock_extractor_class,
            patch(
                "models.rest_api.entitybase.v1.utils.lexeme_term_processor.logger"
            ) as mock_logger,
        ):
            mock_extractor = MagicMock()
            mock_extractor.hash_string.return_value = 12345
            mock_extractor_class.return_value = mock_extractor

            _process_term_data(terms, s3_client, config, None)

            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Failed to store form representation" in call_args
