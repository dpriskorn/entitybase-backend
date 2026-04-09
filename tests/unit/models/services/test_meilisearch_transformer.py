"""Unit tests for Meilisearch transformer."""

import pytest

from models.services.meilisearch.transformer import (
    _flatten_claims,
    transform_to_meilisearch,
)


class TestTransformToMeilisearch:
    """Tests for transform_to_meilisearch function."""

    def test_transform_valid_entity(self):
        """Test transforming a valid entity."""
        entity_json = {
            "entities": {
                "Q42": {
                    "type": "item",
                    "id": "Q42",
                    "lastrevid": 12345,
                    "modified": "2025-01-01T00:00:00Z",
                    "labels": {"en": {"language": "en", "value": "Answer"}},
                    "descriptions": {"en": {"language": "en", "value": "The answer"}},
                    "aliases": {"en": ["Answer", "The answer"]},
                    "claims": {},
                }
            }
        }

        result = transform_to_meilisearch(entity_json)

        assert result.entity_id == "Q42"
        assert result.entity_type == "item"
        assert result.lastrevid == 12345
        assert result.labels == {"en": {"language": "en", "value": "Answer"}}

    def test_transform_empty_entities(self):
        """Test transforming with no entities."""
        entity_json = {"entities": {}}

        result = transform_to_meilisearch(entity_json)

        assert result.entity_id == ""
        assert result.entity_type == ""

    def test_transform_missing_entities_key(self):
        """Test transforming without entities key."""
        entity_json = {}

        result = transform_to_meilisearch(entity_json)

        assert result.entity_id == ""
        assert result.entity_type == ""

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
                        "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}}]
                    },
                }
            }
        }

        result = transform_to_meilisearch(entity_json)

        assert result.entity_id == "Q42"
        assert "P31" in result.claims_flat.data

    def test_transform_lexeme(self):
        """Test transforming a lexeme entity."""
        entity_json = {
            "entities": {
                "L123": {
                    "type": "lexeme",
                    "id": "L123",
                    "lastrevid": 67890,
                    "modified": "2025-01-02T00:00:00Z",
                    "language": "Q1860",
                    "lexicalCategory": "Q1084",
                    "lemmas": {"en": {"language": "en", "value": "test"}},
                    "forms": [],
                    "senses": [],
                    "labels": {},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                }
            }
        }

        result = transform_to_meilisearch(entity_json)

        assert result.entity_id == "L123"
        assert result.lexicalCategory == "Q1084"
        assert result.language == "Q1860"


class TestFlattenClaims:
    """Tests for _flatten_claims function."""

    def test_flatten_claims_entity_reference(self):
        """Test flattening claims with entity references."""
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"id": "Q5", "entity-type": "item"}}
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert result.data["P31"] == ["Q5"]

    def test_flatten_claims_time_value(self):
        """Test flattening claims with time values."""
        claims = {
            "P569": [
                {
                    "mainsnak": {
                        "datavalue": {"value": {"time": "+1980-01-01T00:00:00Z"}}
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert result.data["P569"] == ["+1980-01-01T00:00:00Z"]

    def test_flatten_claims_quantity(self):
        """Test flattening claims with quantity values."""
        claims = {
            "P1111": [
                {"mainsnak": {"datavalue": {"value": {"amount": "42.5", "unit": "1"}}}}
            ]
        }

        result = _flatten_claims(claims)

        assert result.data["P1111"] == ["42.5"]

    def test_flatten_claims_string_value(self):
        """Test flattening claims with string values."""
        claims = {"P1476": [{"mainsnak": {"datavalue": {"value": "Test title"}}}]}

        result = _flatten_claims(claims)

        assert result.data["P1476"] == ["Test title"]

    def test_flatten_claims_multiple_values(self):
        """Test flattening claims with multiple values."""
        claims = {
            "P31": [
                {"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}},
                {"mainsnak": {"datavalue": {"value": {"id": "Q6"}}}},
            ]
        }

        result = _flatten_claims(claims)

        assert result.data["P31"] == ["Q5", "Q6"]

    def test_flatten_claims_empty(self):
        """Test flattening empty claims."""
        claims = {}

        result = _flatten_claims(claims)

        assert result.data == {}

    def test_flatten_claims_no_datavalue(self):
        """Test flattening claims without datavalue."""
        claims = {"P31": [{"mainsnak": {}}]}

        result = _flatten_claims(claims)

        assert "P31" not in result.data

    def test_flatten_claims_snaktype_not_value(self):
        """Test flattening claims with non-value snaktype."""
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "novalue",
                        "datavalue": {"value": {"id": "Q5"}},
                    }
                }
            ]
        }

        result = _flatten_claims(claims)

        assert "P31" not in result.data
