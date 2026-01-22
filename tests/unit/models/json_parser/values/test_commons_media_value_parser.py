"""Unit tests for commons_media_value_parser."""

import pytest

from models.json_parser.values.commons_media_value_parser import parse_commons_media_value
from models.internal_representation.values.commons_media_value import CommonsMediaValue


class TestCommonsMediaValueParser:
    """Unit tests for commons media value parser."""

    def test_parse_valid_commons_media_value(self):
        """Test parsing a valid commons media value."""
        datavalue = {
            "value": "Example.jpg"
        }

        result = parse_commons_media_value(datavalue)

        assert isinstance(result, CommonsMediaValue)
        assert result.kind == "commons_media"
        assert result.value == "Example.jpg"
        assert result.datatype_uri == "http://wikiba.se/ontology#CommonsMedia"

    def test_parse_commons_media_value_with_path(self):
        """Test parsing a commons media value with directory path."""
        datavalue = {
            "value": "Archive/2023-12/Example.png"
        }

        result = parse_commons_media_value(datavalue)

        assert result.value == "Archive/2023-12/Example.png"

    def test_parse_commons_media_value_empty_string(self):
        """Test parsing an empty commons media value."""
        datavalue = {
            "value": ""
        }

        result = parse_commons_media_value(datavalue)

        assert result.value == ""

    def test_parse_commons_media_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_commons_media_value(datavalue)

        assert isinstance(result, CommonsMediaValue)
        assert result.value == ""  # Empty string default

    def test_parse_commons_media_value_special_characters(self):
        """Test parsing a commons media value with special characters."""
        datavalue = {
            "value": "File:Example_(test)_file.jpg"
        }

        result = parse_commons_media_value(datavalue)

        assert result.value == "File:Example_(test)_file.jpg"

    def test_parse_commons_media_value_unicode(self):
        """Test parsing a commons media value with unicode characters."""
        datavalue = {
            "value": "Файл:Пример_файла.jpg"
        }

        result = parse_commons_media_value(datavalue)

        assert result.value == "Файл:Пример_файла.jpg"

    def test_parse_commons_media_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {
            "value": "Example.jpg"
        }

        result = parse_commons_media_value(datavalue)

        assert isinstance(result, CommonsMediaValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_commons_media_value_long_filename(self):
        """Test parsing a commons media value with a very long filename."""
        long_filename = "A_very_long_filename_that_might_cause_issues_with_filesystems_or_databases_but_should_still_be_handled_properly_by_the_parser.jpg"
        datavalue = {
            "value": long_filename
        }

        result = parse_commons_media_value(datavalue)

        assert result.value == long_filename