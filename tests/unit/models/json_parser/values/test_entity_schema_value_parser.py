"""Unit tests for entity_schema_value_parser."""

import pytest

from models.json_parser.values.entity_schema_value_parser import (
    parse_entity_schema_value,
)
from models.internal_representation.values.entity_schema_value import EntitySchemaValue


class TestEntitySchemaValueParser:
    """Unit tests for entity schema value parser."""

    def test_parse_valid_entity_schema_value(self):
        """Test parsing a valid entity schema value."""
        datavalue = {"value": "E123"}

        result = parse_entity_schema_value(datavalue)

        assert isinstance(result, EntitySchemaValue)
        assert result.kind == "entity_schema"
        assert result.value == "E123"
        assert result.datatype_uri == "http://wikiba.se/ontology#EntitySchema"

    def test_parse_entity_schema_value_numeric_id(self):
        """Test parsing an entity schema value with numeric ID."""
        datavalue = {"value": "E456"}

        result = parse_entity_schema_value(datavalue)

        assert result.value == "E456"

    def test_parse_entity_schema_value_empty_string(self):
        """Test parsing an empty entity schema value."""
        datavalue = {"value": ""}

        result = parse_entity_schema_value(datavalue)

        assert result.value == ""

    def test_parse_entity_schema_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_entity_schema_value(datavalue)

        assert isinstance(result, EntitySchemaValue)
        assert result.value == ""  # Empty string default

    def test_parse_entity_schema_value_complex_id(self):
        """Test parsing an entity schema value with complex ID."""
        datavalue = {"value": "E12345"}

        result = parse_entity_schema_value(datavalue)

        assert result.value == "E12345"

    def test_parse_entity_schema_value_unicode_content(self):
        """Test parsing an entity schema value with unicode characters."""
        datavalue = {"value": "E123_测试"}

        result = parse_entity_schema_value(datavalue)

        assert result.value == "E123_测试"

    def test_parse_entity_schema_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "E123"}

        result = parse_entity_schema_value(datavalue)

        assert isinstance(result, EntitySchemaValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_entity_schema_value_special_characters(self):
        """Test parsing an entity schema value with special characters."""
        datavalue = {"value": "E123-test_schema"}

        result = parse_entity_schema_value(datavalue)

        assert result.value == "E123-test_schema"
