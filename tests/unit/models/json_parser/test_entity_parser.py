"""Unit tests for entity_parser."""

import json
from pathlib import Path

from models.internal_representation.entity_data import EntityData
from models.internal_representation.lexeme import LexemeForm, LexemeSense
from models.json_parser.entity_parser import parse_entity, parse_entity_data


class TestEntityParser:
    """Unit tests for entity parser."""

    

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

    

        assert result.lemmas is not None
        assert result.lemmas["en"]["value"] == "be"
        assert result.lexical_category == "Q24905"  # verb
        assert result.language == "Q1860"  # English

    
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