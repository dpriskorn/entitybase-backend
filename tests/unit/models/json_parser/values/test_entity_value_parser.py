"""Unit tests for entity_value_parser."""

import pytest

from models.json_parser.values.entity_value_parser import parse_entity_value
from models.internal_representation.values.entity_value import EntityValue


class TestEntityValueParser:
    """Unit tests for entity value parser."""

    def test_parse_valid_entity_value(self):
        """Test parsing a valid entity value."""
        datavalue = {"value": {"id": "Q42"}}

        result = parse_entity_value(datavalue)

        assert isinstance(result, EntityValue)
        assert result.kind == "entity"
        assert result.value == "Q42"
        assert result.datatype_uri == "http://wikiba.se/ontology#WikibaseItem"

    def test_parse_entity_value_qid(self):
        """Test parsing an entity value with QID."""
        datavalue = {"value": {"id": "Q123456"}}

        result = parse_entity_value(datavalue)

        assert result.value == "Q123456"

    def test_parse_entity_value_pid(self):
        """Test parsing an entity value with property ID."""
        datavalue = {"value": {"id": "P31"}}

        result = parse_entity_value(datavalue)

        assert result.value == "P31"

    def test_parse_entity_value_lid(self):
        """Test parsing an entity value with lexeme ID."""
        datavalue = {"value": {"id": "L123"}}

        result = parse_entity_value(datavalue)

        assert result.value == "L123"

    def test_parse_entity_value_missing_id(self):
        """Test parsing when entity ID is missing from value dict."""
        datavalue = {
            "value": {
                # No "id" field
            }
        }

        result = parse_entity_value(datavalue)

        assert isinstance(result, EntityValue)
        assert result.value == ""  # Empty string default

    def test_parse_entity_value_missing_value_dict(self):
        """Test parsing when the value dict is missing."""
        datavalue = {}

        result = parse_entity_value(datavalue)

        assert isinstance(result, EntityValue)
        assert result.value == ""  # Empty string default

    def test_parse_entity_value_empty_id(self):
        """Test parsing an entity value with empty ID."""
        datavalue = {"value": {"id": ""}}

        result = parse_entity_value(datavalue)

        assert result.value == ""

    def test_parse_entity_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": {"id": "Q42"}}

        result = parse_entity_value(datavalue)

        assert isinstance(result, EntityValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_entity_value_numeric_id(self):
        """Test parsing an entity value with numeric ID."""
        datavalue = {
            "value": {
                "id": "123"  # Just numeric, no prefix
            }
        }

        result = parse_entity_value(datavalue)

        assert result.value == "123"
