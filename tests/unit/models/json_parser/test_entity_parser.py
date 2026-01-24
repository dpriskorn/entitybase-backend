"""Unit tests for entity_parser."""

from models.internal_representation.entity_data import EntityData
from models.json_parser.entity_parser import parse_entity, parse_entity_data


class TestEntityParser:
    """Unit tests for entity parser."""

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