"""Unit tests for value_formatters."""

import pytest
from unittest.mock import MagicMock

from models.rdf_builder.value_formatters import ValueFormatter
from models.internal_representation.value_kinds import ValueKind


class TestValueFormatter:
    """Unit tests for ValueFormatter."""

    def test_format_value_entity(self) -> None:
        """Test formatting entity values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.ENTITY
        mock_value.value = "Q42"

        result = ValueFormatter.format_value(mock_value)
        assert result == "wd:Q42"

    def test_format_value_string(self) -> None:
        """Test formatting string values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.STRING
        mock_value.value = "Hello World"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"Hello World"'

    def test_format_value_string_with_quotes(self) -> None:
        """Test formatting string values with quotes."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.STRING
        mock_value.value = 'He said "Hello"'

        result = ValueFormatter.format_value(mock_value)
        assert result == '"He said \\"Hello\\""'

    def test_format_value_time(self) -> None:
        """Test formatting time values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.TIME
        mock_value.value = "+2023-12-25T00:00:00Z"

        result = ValueFormatter.format_value(mock_value)
        expected = f'"{mock_value.value}"^^xsd:dateTime'
        assert result == expected

    def test_format_value_quantity(self) -> None:
        """Test formatting quantity values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.QUANTITY
        mock_value.value = "42.5"

        result = ValueFormatter.format_value(mock_value)
        assert result == "42.5^^xsd:decimal"

    def test_format_value_globe(self) -> None:
        """Test formatting globe (coordinate) values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.GLOBE
        mock_value.latitude = 40.7128
        mock_value.longitude = -74.0060

        result = ValueFormatter.format_value(mock_value)
        assert result == '"Point(-74.006 40.7128)"^^geo:wktLiteral'

    def test_format_value_monolingual(self) -> None:
        """Test formatting monolingual text values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.MONOLINGUAL
        mock_value.text = "Hello"
        mock_value.language = "en"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"Hello"@en'

    def test_format_value_monolingual_with_quotes(self) -> None:
        """Test formatting monolingual values with quotes."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.MONOLINGUAL
        mock_value.text = 'He said "Hello"'
        mock_value.language = "en"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"He said \\"Hello\\""@en'

    def test_format_value_external_id(self) -> None:
        """Test formatting external ID values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.EXTERNAL_ID
        mock_value.value = "ISBN 978-0-123456-78-9"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"ISBN 978-0-123456-78-9"'

    def test_format_value_commons_media(self) -> None:
        """Test formatting Commons media values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.COMMONS_MEDIA
        mock_value.value = "Example.jpg"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"Example.jpg"'

    def test_format_value_geo_shape(self) -> None:
        """Test formatting geo shape values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.GEO_SHAPE
        mock_value.value = "Data:World_Map.svg"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"Data:World_Map.svg"'

    def test_format_value_url(self) -> None:
        """Test formatting URL values."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.URL
        mock_value.value = "https://www.wikidata.org"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"https://www.wikidata.org"'

    def test_format_value_novalue(self) -> None:
        """Test formatting novalue."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.NOVALUE

        result = ValueFormatter.format_value(mock_value)
        assert result == "wikibase:noValue"

    def test_format_value_somevalue(self) -> None:
        """Test formatting somevalue."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.SOMEVALUE

        result = ValueFormatter.format_value(mock_value)
        assert result == "wikibase:someValue"

    def test_format_value_unsupported_type(self) -> None:
        """Test formatting unsupported value types."""
        # Test some of the types not explicitly handled
        mock_value = MagicMock()
        mock_value.kind = ValueKind.TABULAR_DATA
        mock_value.value = "some_data"

        result = ValueFormatter.format_value(mock_value)
        assert result == ""  # Empty string for unsupported types

    def test_escape_turtle_basic(self) -> None:
        """Test basic Turtle escaping."""
        result = ValueFormatter.escape_turtle("Hello World")
        assert result == "Hello World"

    def test_escape_turtle_backslash(self) -> None:
        """Test escaping backslashes."""
        result = ValueFormatter.escape_turtle("path\\to\\file")
        assert result == "path\\\\to\\\\file"

    def test_escape_turtle_quotes(self) -> None:
        """Test escaping quotes."""
        result = ValueFormatter.escape_turtle('He said "Hello"')
        assert result == 'He said \\"Hello\\"'

    def test_escape_turtle_newlines(self) -> None:
        """Test escaping newlines."""
        result = ValueFormatter.escape_turtle("Line 1\nLine 2")
        assert result == "Line 1\\nLine 2"

    def test_escape_turtle_carriage_returns(self) -> None:
        """Test escaping carriage returns."""
        result = ValueFormatter.escape_turtle("Line 1\rLine 2")
        assert result == "Line 1\\rLine 2"

    def test_escape_turtle_tabs(self) -> None:
        """Test escaping tabs."""
        result = ValueFormatter.escape_turtle("Col1\tCol2")
        assert result == "Col1\\tCol2"

    def test_escape_turtle_multiple_chars(self) -> None:
        """Test escaping multiple special characters."""
        result = ValueFormatter.escape_turtle('Text with "quotes"\nand\ttabs\r\n')
        assert result == 'Text with \\"quotes\\"\\nand\\ttabs\\r\\n'

    def test_escape_turtle_empty_string(self) -> None:
        """Test escaping empty string."""
        result = ValueFormatter.escape_turtle("")
        assert result == ""

    def test_escape_turtle_no_special_chars(self) -> None:
        """Test escaping string with no special characters."""
        result = ValueFormatter.escape_turtle("NormalText123")
        assert result == "NormalText123"

    def test_format_value_with_special_chars_in_string(self) -> None:
        """Test that string formatting properly escapes special characters."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.STRING
        mock_value.value = 'String with "quotes" and\ttabs\n'

        result = ValueFormatter.format_value(mock_value)
        assert result == '"String with \\"quotes\\" and\\ttabs\\n"'

    def test_format_value_with_special_chars_in_monolingual(self) -> None:
        """Test that monolingual formatting properly escapes special characters."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.MONOLINGUAL
        mock_value.text = 'Text with "quotes"'
        mock_value.language = "en"

        result = ValueFormatter.format_value(mock_value)
        assert result == '"Text with \\"quotes\\""@en'

    def test_format_value_with_special_chars_in_external_id(self) -> None:
        """Test that external ID formatting properly escapes special characters."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.EXTERNAL_ID
        mock_value.value = 'ID with "quotes"'

        result = ValueFormatter.format_value(mock_value)
        assert result == '"ID with \\"quotes\\""'

    def test_format_value_with_special_chars_in_url(self) -> None:
        """Test that URL formatting properly escapes special characters."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.URL
        mock_value.value = 'http://example.com/path with "quotes"'

        result = ValueFormatter.format_value(mock_value)
        assert result == '"http://example.com/path with \\"quotes\\""'

    def test_format_value_with_special_chars_in_commons_media(self) -> None:
        """Test that Commons media formatting properly escapes special characters."""
        mock_value = MagicMock()
        mock_value.kind = ValueKind.COMMONS_MEDIA
        mock_value.value = 'File:Example "test".jpg'

        result = ValueFormatter.format_value(mock_value)
        assert result == '"File:Example \\"test\\".jpg"'