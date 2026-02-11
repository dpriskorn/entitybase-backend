"""Unit tests for url_value_parser."""

import pytest

from models.json_parser.values.url_value_parser import parse_url_value
from models.internal_representation.values.url_value import URLValue


class TestUrlValueParser:
    """Unit tests for URL value parser."""

    def test_parse_valid_url_value(self):
        """Test parsing a valid URL value."""
        datavalue = {"value": "https://www.wikidata.org/wiki/Q42"}

        result = parse_url_value(datavalue)

        assert isinstance(result, URLValue)
        assert result.kind == "url"
        assert result.value == "https://www.wikidata.org/wiki/Q42"
        assert result.datatype_uri == "http://wikiba.se/ontology#Url"

    def test_parse_url_value_http(self):
        """Test parsing a URL value with HTTP protocol."""
        datavalue = {"value": "http://example.com/path"}

        result = parse_url_value(datavalue)

        assert result.value == "http://example.com/path"

    def test_parse_url_value_ftp(self):
        """Test parsing a URL value with FTP protocol."""
        datavalue = {"value": "ftp://ftp.example.com/file.txt"}

        result = parse_url_value(datavalue)

        assert result.value == "ftp://ftp.example.com/file.txt"

    def test_parse_url_value_without_protocol(self):
        """Test parsing a URL-like string without protocol."""
        datavalue = {"value": "www.example.com"}

        result = parse_url_value(datavalue)

        assert result.value == "www.example.com"

    def test_parse_url_value_empty_string(self):
        """Test parsing an empty URL value."""
        datavalue = {"value": ""}

        result = parse_url_value(datavalue)

        assert result.value == ""

    def test_parse_url_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_url_value(datavalue)

        assert isinstance(result, URLValue)
        assert result.value == ""  # Empty string default

    def test_parse_url_value_complex_url(self):
        """Test parsing a complex URL with query parameters."""
        datavalue = {
            "value": "https://www.example.com/path/to/resource?param1=value1&param2=value2#fragment"
        }

        result = parse_url_value(datavalue)

        assert (
            result.value
            == "https://www.example.com/path/to/resource?param1=value1&param2=value2#fragment"
        )

    def test_parse_url_value_unicode(self):
        """Test parsing a URL with unicode characters."""
        datavalue = {"value": "https://例え.テスト/パス"}

        result = parse_url_value(datavalue)

        assert result.value == "https://例え.テスト/パス"

    def test_parse_url_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "https://www.wikidata.org"}

        result = parse_url_value(datavalue)

        assert isinstance(result, URLValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_url_value_relative_path(self):
        """Test parsing a relative URL path."""
        datavalue = {"value": "/wiki/Main_Page"}

        result = parse_url_value(datavalue)

        assert result.value == "/wiki/Main_Page"
