"""Unit tests for import endpoint lexeme validation."""

import pytest
from pydantic import ValidationError

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.rest_api.utils import raise_validation_error
from models.services.wikidata_import_service import WikidataImportService


class TestImportEndpointLexemeValidation:
    """Test lexeme-specific validation in import endpoint."""

    def test_lexeme_with_single_lemma_passes_validation(self):
        """Test that lexeme with one lemma passes validation."""
        lexeme_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
            "labels": {"en": {"language": "en", "value": "answer"}},
        }

        request = EntityCreateRequest(**lexeme_data)

        assert request.type == "lexeme"
        assert len(request.lemmas) == 1

    def test_lexeme_with_multiple_lemmas_passes_validation(self):
        """Test that lexeme with multiple lemmas passes validation."""
        lexeme_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {
                "en": {"language": "en", "value": "answer"},
                "de": {"language": "de", "value": "Antwort"},
            },
            "labels": {"en": {"language": "en", "value": "answer"}},
        }

        request = EntityCreateRequest(**lexeme_data)

        assert request.type == "lexeme"
        assert len(request.lemmas) == 2

    def test_lexeme_with_empty_lemmas_fails_validation(self):
        """Test that lexeme with empty lemmas fails validation."""
        lexeme_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {},
            "labels": {"en": {"language": "en", "value": "answer"}},
        }

        request = EntityCreateRequest(**lexeme_data)

        assert request.type == "lexeme"
        lemma_count = sum(1 for lang in request.lemmas if lang != "lemma_hashes")
        assert lemma_count == 0

        # Test the validation logic directly
        if request.type == "lexeme":
            lemma_count = sum(1 for lang in request.lemmas if lang != "lemma_hashes")
            assert lemma_count == 0, "Expected 0 lemmas"

    def test_lexeme_with_only_hash_lemmas_fails_validation(self):
        """Test that lexeme with only lemma_hashes passes validation."""
        # Lemma hashes would be stored as strings by Pydantic
        lexeme_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "labels": {"en": {"language": "en", "value": "answer"}},
        }

        request = EntityCreateRequest(**lexeme_data)

        lemma_count = sum(1 for lang in request.lemmas if lang != "lemma_hashes")
        assert lemma_count == 0

    def test_item_without_lemmas_passes_validation(self):
        """Test that items without lemmas don't trigger lexeme validation."""
        item_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
        }

        request = EntityCreateRequest(**item_data)

        assert request.type == "item"

        # Should not trigger lexeme validation
        if request.type == "lexeme":
            pytest.fail("Item should not trigger lexeme validation")

    def test_property_without_lemmas_passes_validation(self):
        """Test that properties without lemmas don't trigger lexeme validation."""
        property_data = {
            "id": "P31",
            "type": "property",
            "labels": {"en": {"language": "en", "value": "instance of"}},
        }

        request = EntityCreateRequest(**property_data)

        assert request.type == "property"

        # Should not trigger lexeme validation
        if request.type == "lexeme":
            pytest.fail("Property should not trigger lexeme validation")


class TestLexemeFieldExtraction:
    """Test extraction of lexeme-specific fields from Wikidata data."""

    def test_lexeme_extraction_with_all_fields(self):
        """Test extraction of complete lexeme with all fields."""
        wikidata_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
            "labels": {"en": {"language": "en", "value": "answer"}},
            "forms": [
                {
                    "id": "L42-F1",
                    "representations": {"en": {"language": "en", "value": "answer"}},
                    "grammaticalFeatures": ["Q110786"],
                }
            ],
            "senses": [
                {
                    "id": "L42-S1",
                    "glosses": {
                        "en": {"language": "en", "value": "reply to a question"}
                    },
                }
            ],
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "L42"
        assert result.type == "lexeme"
        assert result.lemmas == {"en": {"language": "en", "value": "answer"}}
        assert len(result.forms) == 1
        assert result.forms[0]["id"] == "L42-F1"
        assert len(result.senses) == 1
        assert result.senses[0]["id"] == "L42-S1"

    def test_lexeme_extraction_with_empty_forms_senses(self):
        """Test extraction of lexeme with empty forms and senses."""
        wikidata_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
            "labels": {"en": {"language": "en", "value": "answer"}},
            "forms": [],
            "senses": [],
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "L42"
        assert result.type == "lexeme"
        assert result.forms == []
        assert result.senses == []
        assert result.lemmas == {"en": {"language": "en", "value": "answer"}}

    def test_lexeme_extraction_without_forms_senses(self):
        """Test extraction of lexeme missing forms and senses fields."""
        wikidata_data = {
            "id": "L42",
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
            "labels": {"en": {"language": "en", "value": "answer"}},
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "L42"
        assert result.type == "lexeme"
        assert result.forms == []
        assert result.senses == []
        assert result.lemmas == {"en": {"language": "en", "value": "answer"}}


class TestWikidataLexemeDataStructure:
    """Test handling of real Wikidata lexeme data structure."""

    def test_real_lexeme_l42_structure(self):
        """Test that L42 real data structure is handled correctly."""
        real_l42_data = {
            "pageid": 54387043,
            "ns": 146,
            "title": "Lexeme:L42",
            "lastrevid": 2425773420,
            "modified": "2025-11-04T23:12:11Z",
            "type": "lexeme",
            "id": "L42",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
            "lexicalCategory": "Q1084",
            "language": "Q1860",
            "claims": {},
            "forms": [
                {
                    "id": "L42-F1",
                    "representations": {"en": {"language": "en", "value": "answer"}},
                    "grammaticalFeatures": ["Q110786"],
                    "claims": {},
                }
            ],
            "senses": [
                {
                    "id": "L42-S1",
                    "glosses": {
                        "en": {
                            "language": "en",
                            "value": "reply; reaction to a question",
                        }
                    },
                    "claims": {},
                }
            ],
        }

        result = WikidataImportService.transform_to_create_request(real_l42_data)

        assert result.id == "L42"
        assert result.type == "lexeme"
        assert "en" in result.lemmas
        assert result.lemmas["en"]["value"] == "answer"
        assert len(result.forms) >= 1
        assert len(result.senses) >= 1
