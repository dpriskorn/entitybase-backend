"""Unit tests for monolingual_value_parser."""

import pytest

from models.internal_representation.values.monolingual_value import MonolingualValue
from models.json_parser.values.monolingual_value_parser import parse_monolingual_value


class TestMonolingualValueParser:
    """Unit tests for monolingual value parser."""

    def test_parse_valid_monolingual_value(self):
        """Test parsing a valid monolingual value."""
        datavalue = {"value": {"language": "en", "text": "Hello World"}}

        result = parse_monolingual_value(datavalue)

        assert isinstance(result, MonolingualValue)
        assert result.kind == "monolingual"
        assert result.value == ""  # Always empty string
        assert result.language == "en"
        assert result.text == "Hello World"
        assert result.datatype_uri == "http://wikiba.se/ontology#MonolingualText"

    def test_parse_monolingual_value_with_special_characters(self):
        """Test parsing monolingual value with special characters."""
        datavalue = {"value": {"language": "es", "text": "¡Hola, mundo! ¿Cómo estás?"}}

        result = parse_monolingual_value(datavalue)

        assert result.language == "es"
        assert result.text == "¡Hola, mundo! ¿Cómo estás?"

    def test_parse_monolingual_value_unicode_text(self):
        """Test parsing monolingual value with unicode text."""
        datavalue = {"value": {"language": "zh", "text": "你好世界"}}

        result = parse_monolingual_value(datavalue)

        assert result.language == "zh"
        assert result.text == "你好世界"

    def test_parse_monolingual_value_missing_language(self):
        """Test parsing when language field is missing."""
        datavalue = {"value": {"text": "Some text"}}

        result = parse_monolingual_value(datavalue)

        assert result.language == ""  # Empty string default
        assert result.text == "Some text"

    def test_parse_monolingual_value_missing_text(self):
        """Test parsing when text field is missing."""
        datavalue = {"value": {"language": "fr"}}

        result = parse_monolingual_value(datavalue)

        assert result.language == "fr"
        assert result.text == ""  # Empty string default

    def test_parse_monolingual_value_empty_fields(self):
        """Test parsing with empty language and text."""
        datavalue = {"value": {"language": "", "text": ""}}

        result = parse_monolingual_value(datavalue)

        assert result.language == ""
        assert result.text == ""

    def test_parse_monolingual_value_missing_value_dict(self):
        """Test parsing when the value dict is missing."""
        datavalue = {}

        result = parse_monolingual_value(datavalue)

        assert isinstance(result, MonolingualValue)
        assert result.language == ""  # Empty string default
        assert result.text == ""  # Empty string default

    def test_parse_monolingual_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": {"language": "de", "text": "Hallo Welt"}}

        result = parse_monolingual_value(datavalue)

        assert isinstance(result, MonolingualValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.language = "modified"

    def test_parse_monolingual_value_with_tabs_and_spaces(self):
        """Test parsing monolingual value with tabs and multiple spaces."""
        datavalue = {
            "value": {
                "language": "en",
                "text": "Text\twith\ttabs  and  multiple   spaces",
            }
        }

        result = parse_monolingual_value(datavalue)

        assert (
            result.text == "Text\twith\ttabs  and  multiple   spaces"
        )  # Whitespace preserved
