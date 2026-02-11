"""Unit tests for string_value_parser."""

import pytest

from models.json_parser.values.string_value_parser import parse_string_value
from models.internal_representation.values.string_value import StringValue


class TestStringValueParser:
    """Unit tests for string value parser."""

    def test_parse_valid_string_value(self):
        """Test parsing a valid string value."""
        datavalue = {"value": "Hello World"}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.kind == "string"
        assert result.value == "Hello World"
        assert result.datatype_uri == "http://wikiba.se/ontology#String"

    def test_parse_empty_string_value(self):
        """Test parsing an empty string value."""
        datavalue = {"value": ""}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == ""

    def test_parse_unicode_string_value(self):
        """Test parsing a string value with Unicode characters."""
        datavalue = {"value": "Hello 世界 🌍"}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == "Hello 世界 🌍"

    def test_parse_missing_value_field(self):
        """Test parsing when value field is missing."""
        datavalue = {}  # Missing value field

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == ""  # Should default to empty string

    def test_parse_none_value_field(self):
        """Test parsing when value field is None."""
        datavalue = {"value": None}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == ""  # None should become empty string

    def test_parse_numeric_value_as_string(self):
        """Test parsing when value is numeric (should be converted to string)."""
        datavalue = {"value": 12345}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == "12345"  # Numeric converted to string

    def test_parse_boolean_value_as_string(self):
        """Test parsing when value is boolean."""
        datavalue = {"value": True}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == "True"  # Boolean converted to string

    def test_parse_complex_datavalue_structure(self):
        """Test parsing with additional fields in datavalue (should ignore them)."""
        datavalue = {"value": "test string", "type": "string", "extra_field": "ignored"}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        assert result.value == "test string"

    def test_parse_result_is_frozen(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "immutable"}

        result = parse_string_value(datavalue)

        assert isinstance(result, StringValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"
