"""Unit tests for entity_parser."""

import json
from pathlib import Path

from models.internal_representation.entity_data import EntityData
from models.internal_representation.lexeme import LexemeForm, LexemeSense
from models.json_parser.entity_parser import parse_entity, parse_entity_data


class TestEntityParser:
    """Unit tests for entity parser."""

    def test_parse_lexeme_l42(self) -> None:
        """Test parsing lexeme L42 from test data."""
        test_data_path = Path(__file__).parent.parent.parent.parent / "test_data" / "json" / "entities" / "L42.json"

        with open(test_data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        result = parse_entity_data(raw_data)

        assert isinstance(result, EntityData)
        assert result.id == "L42"
        assert result.type == "lexeme"

        # Check lexeme-specific fields
        assert result.lemmas is not None
        assert "en" in result.lemmas
        assert result.lemmas["en"]["value"] == "answer"

        assert result.lexical_category == "Q1084"
        assert result.language == "Q1860"

        # Check forms
        assert result.forms is not None
        assert len(result.forms) == 3

        # Check first form (L42-F1)
        form1 = result.forms[0]
        assert isinstance(form1, LexemeForm)
        assert form1.id == "L42-F1"
        assert "en" in form1.representations
        assert form1.representations["en"].value == "answer"
        assert "Q110786" in form1.grammatical_features

        # Check second form (L42-F2)
        form2 = result.forms[1]
        assert form2.id == "L42-F2"
        assert form2.representations["en"].value == "answers"

        # Check third form (L42-F4)
        form3 = result.forms[2]
        assert form3.id == "L42-F4"
        assert form3.representations["en"].value == "answer's"

        # Check senses
        assert result.senses is not None
        assert len(result.senses) == 3

        # Check first sense (L42-S1)
        sense1 = result.senses[0]
        assert isinstance(sense1, LexemeSense)
        assert sense1.id == "L42-S1"
        assert "en" in sense1.glosses
        assert "reply; reaction to a question" in sense1.glosses["en"].value

        # Check second sense (L42-S2)
        sense2 = result.senses[1]
        assert sense2.id == "L42-S2"
        assert sense2.glosses["en"].value == "solution to a problem"

        # Check third sense (L42-S3)
        sense3 = result.senses[2]
        assert sense3.id == "L42-S3"
        assert sense3.glosses["en"].value == "result, outcome"

        # Check that statements are parsed
        assert len(result.statements) > 0

        # Check sitelinks (should be empty for lexemes typically)
        assert result.sitelinks == {}

    def test_parse_lexeme_l1883(self) -> None:
        """Test parsing lexeme L1883 from test data."""
        test_data_path = Path(__file__).parent.parent.parent.parent / "test_data" / "json" / "entities" / "L1883.json"

        with open(test_data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        result = parse_entity_data(raw_data)

        assert isinstance(result, EntityData)
        assert result.id == "L1883"
        assert result.type == "lexeme"

        assert result.lemmas is not None
        assert result.lemmas["en"]["value"] == "be"
        assert result.lexical_category == "Q24905"  # verb
        assert result.language == "Q1860"  # English

    def test_parse_item_q42(self) -> None:
        """Test parsing regular item still works."""
        # Mock item data
        item_data = {
            "id": "Q42",
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Test Item"}
            },
            "descriptions": {
                "en": {"language": "en", "value": "A test item"}
            },
            "aliases": {
                "en": [{"language": "en", "value": "Test"}]
            },
            "claims": {
                "P31": [{
                    "mainsnak": {
                        "property": "P31",
                        "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}
                    },
                    "rank": "normal",
                    "type": "statement"
                }]
            },
            "sitelinks": {
                "enwiki": {"site": "enwiki", "title": "Test"}
            }
        }

        result = parse_entity_data(item_data)

        assert isinstance(result, EntityData)
        assert result.id == "Q42"
        assert result.type == "item"

        # Lexeme fields should be empty/default for items
        assert result.lemmas is None
        assert result.lexical_category == ""
        assert result.language == ""
        assert result.forms is None
        assert result.senses is None

        # Regular fields should work
        assert "en" in result.labels
        assert result.labels["en"]["value"] == "Test Item"
        assert len(result.statements) == 1
        assert result.sitelinks == {"enwiki": {"site": "enwiki", "title": "Test"}}

    def test_parse_lexeme_minimal(self) -> None:
        """Test parsing minimal lexeme with just required fields."""
        minimal_lexeme = {
            "id": "L1",
            "type": "lexeme",
            "lemmas": {
                "en": {"language": "en", "value": "test"}
            },
            "lexicalCategory": "Q1084",
            "language": "Q1860"
        }

        result = parse_entity_data(minimal_lexeme)

        assert isinstance(result, EntityData)
        assert result.id == "L1"
        assert result.type == "lexeme"
        assert result.lemmas["en"]["value"] == "test"
        assert result.lexical_category == "Q1084"
        assert result.language == "Q1860"

        # Optional fields should be None/empty
        assert result.forms == []
        assert result.senses == []
        assert result.statements == []

    def test_parse_nested_entity_structure(self) -> None:
        """Test parsing entity with nested Wikidata API structure."""
        nested_data = {
            "entities": {
                "L42": {
                    "id": "L42",
                    "type": "lexeme",
                    "lemmas": {
                        "en": {"language": "en", "value": "test"}
                    },
                    "lexicalCategory": "Q1084",
                    "language": "Q1860",
                    "forms": [],
                    "senses": []
                }
            }
        }

        result = parse_entity_data(nested_data)

        assert isinstance(result, EntityData)
        assert result.id == "L42"
        assert result.type == "lexeme"
        assert result.lemmas["en"]["value"] == "test"

    def test_parse_entity_basic(self) -> None:
        """Test parsing entity with parse_entity function."""
        entity_data = {
            "id": "Q42",
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Test Item"}
            },
            "descriptions": {
                "en": {"language": "en", "value": "A test item"}
            },
            "aliases": {
                "en": [{"language": "en", "value": "Test"}]
            },
            "claims": {
                "P31": [{
                    "mainsnak": {
                        "property": "P31",
                        "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}
                    },
                    "rank": "normal",
                    "type": "statement"
                }]
            },
            "sitelinks": {
                "enwiki": {"site": "enwiki", "title": "Test"}
            }
        }

        result = parse_entity(entity_data)

        assert result.id == "Q42"
        assert result.type == "item"
        assert result.labels.data["en"].value == "Test Item"
        assert result.descriptions.data["en"].value == "A test item"
        assert len(result.aliases.data["en"]) == 1
        assert result.aliases.data["en"][0].value == "Test"
        assert len(result.statements.data) == 1
        assert result.sitelinks.data["enwiki"]["title"] == "Test"

    def test_parse_entity_nested_structure(self) -> None:
        """Test parsing entity with nested Wikidata API structure."""
        nested_data = {
            "entities": {
                "Q42": {
                    "id": "Q42",
                    "type": "item",
                    "labels": {
                        "en": {"language": "en", "value": "Test Item"}
                    },
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                    "sitelinks": {}
                }
            }
        }

        result = parse_entity(nested_data)

        assert result.id == "Q42"
        assert result.type == "item"
        assert result.labels.data["en"].value == "Test Item"