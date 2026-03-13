"""Unit tests for Elasticsearch transformer."""

import pytest

from models.data.infrastructure.elasticsearch import (
    ElasticsearchDocument,
    FlattenedClaims,
)
from models.services.elasticsearch.transformer import (
    _flatten_claims,
    transform_to_elasticsearch,
)


class TestTransformToElasticsearch:
    """Tests for transform_to_elasticsearch function."""

    def test_transform_item(self):
        """Test transforming an item entity."""
        entity_json = {
            "entities": {
                "Q42": {
                    "type": "item",
                    "id": "Q42",
                    "lastrevid": 12345,
                    "modified": "2025-01-01T00:00:00Z",
                    "labels": {"en": {"language": "en", "value": "Test"}},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                }
            }
        }

        result = transform_to_elasticsearch(entity_json)

        assert result.entity_id == "Q42"
        assert result.entity_type == "item"
        assert result.lastrevid == 12345
        assert result.modified == "2025-01-01T00:00:00Z"
        assert result.labels == {"en": {"language": "en", "value": "Test"}}

    def test_transform_property(self):
        """Test transforming a property entity."""
        entity_json = {
            "entities": {
                "P31": {
                    "type": "property",
                    "id": "P31",
                    "datatype": "wikibase-item",
                    "lastrevid": 12345,
                    "modified": "2025-01-01T00:00:00Z",
                    "labels": {"en": {"language": "en", "value": "instance of"}},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                }
            }
        }

        result = transform_to_elasticsearch(entity_json)

        assert result.entity_id == "P31"
        assert result.entity_type == "property"
        assert result.datatype == "wikibase-item"

    def test_transform_lexeme(self):
        """Test transforming a lexeme entity."""
        entity_json = {
            "entities": {
                "L42": {
                    "type": "lexeme",
                    "id": "L42",
                    "language": "Q1860",
                    "lexicalCategory": "Q1084",
                    "lastrevid": 12345,
                    "modified": "2025-01-01T00:00:00Z",
                    "lemmas": {"en": {"language": "en", "value": "test"}},
                    "forms": [],
                    "senses": [],
                    "claims": {},
                }
            }
        }

        result = transform_to_elasticsearch(entity_json)

        assert result.entity_id == "L42"
        assert result.entity_type == "lexeme"
        assert result.language == "Q1860"
        assert result.lexicalCategory == "Q1084"
        assert result.lemmas == {"en": {"language": "en", "value": "test"}}

    def test_transform_empty_entities(self):
        """Test transforming with empty entities."""
        entity_json = {}

        result = transform_to_elasticsearch(entity_json)

        assert result.entity_id == ""
        assert result.entity_type == ""
        assert result.lastrevid == 0

    def test_transform_with_claims(self):
        """Test transforming entity with claims."""
        entity_json = {
            "entities": {
                "Q42": {
                    "type": "item",
                    "id": "Q42",
                    "lastrevid": 12345,
                    "modified": "2025-01-01T00:00:00Z",
                    "labels": {},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {
                        "P31": [
                            {
                                "mainsnak": {
                                    "snaktype": "value",
                                    "property": "P31",
                                    "datavalue": {
                                        "value": {"id": "Q5", "entity-type": "item"},
                                        "type": "wikibase-entityid",
                                    },
                                }
                            }
                        ]
                    },
                }
            }
        }

        result = transform_to_elasticsearch(entity_json)

        assert result.claims_flat == FlattenedClaims(data={"P31": ["Q5"]})
        assert result.claims is not None


class TestFlattenClaims:
    """Tests for _flatten_claims function."""

    def test_flatten_item_claim(self):
        """Test flattening item claims."""
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"id": "Q5", "entity-type": "item"},
                            "type": "wikibase-entityid",
                        },
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert result == FlattenedClaims(data={"P31": ["Q5"]})

    def test_flatten_multiple_values(self):
        """Test flattening claims with multiple values."""
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"id": "Q5", "entity-type": "item"},
                            "type": "wikibase-entityid",
                        },
                    }
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"id": "Q6", "entity-type": "item"},
                            "type": "wikibase-entityid",
                        },
                    }
                },
            ]
        }

        result = _flatten_claims(claims)

        assert result == FlattenedClaims(data={"P31": ["Q5", "Q6"]})

    def test_flatten_time_value(self):
        """Test flattening time value claims."""
        claims = {
            "P569": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P569",
                        "datavalue": {
                            "value": {
                                "time": "+1952-03-11T00:00:00Z",
                                "timezone": 0,
                                "before": 0,
                                "after": 0,
                                "precision": 11,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                            },
                            "type": "time",
                        },
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert result == FlattenedClaims(data={"P569": ["+1952-03-11T00:00:00Z"]})

    def test_flatten_string_value(self):
        """Test flattening string value claims."""
        claims = {
            "P5275": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P5275",
                        "datavalue": {
                            "value": "12345",
                            "type": "string",
                        },
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert result == FlattenedClaims(data={"P5275": ["12345"]})

    def test_flatten_novalue_snaktype(self):
        """Test that novalue snaktype is skipped."""
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "novalue",
                        "property": "P31",
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert result == FlattenedClaims(data={})

    def test_flatten_empty_claims(self):
        """Test flattening empty claims."""
        result = _flatten_claims({})

        assert result == FlattenedClaims(data={})
