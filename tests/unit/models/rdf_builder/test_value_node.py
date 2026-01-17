import pytest
from unittest.mock import MagicMock, patch

pytestmark = pytest.mark.unit

from models.rdf_builder.value_node import (
    _format_scientific_notation,
    generate_value_node_uri,
    serialize_value,
)


class TestFormatScientificNotation:
    def test_format_scientific_notation_with_leading_zero(self):
        """Test formatting removes leading zero in negative exponent."""
        result = _format_scientific_notation(1.0e-5)
        assert result == "1.0E-5"

    def test_format_scientific_notation_with_leading_zero_positive(self):
        """Test formatting removes leading zero in positive exponent."""
        result = _format_scientific_notation(1.0e5)
        assert result == "1.0E+5"

    def test_format_scientific_notation_without_leading_zero(self):
        """Test formatting when no leading zero to remove."""
        result = _format_scientific_notation(1.23e10)
        assert result == "1.2E+10"

    def test_format_scientific_notation_negative_mantissa(self):
        """Test formatting with negative mantissa."""
        result = _format_scientific_notation(-1.0e-5)
        assert result == "-1.0E-5"

    def test_format_scientific_notation_no_match(self):
        """Test formatting when regex doesn't match."""
        result = _format_scientific_notation(123.45)
        assert result == "1.2E+2"


class TestGenerateValueNodeUri:
    def test_generate_value_node_uri_string(self):
        """Test URI generation for string value."""
        result = generate_value_node_uri("test")
        assert len(result) == 32  # MD5 hash length
        assert result.isalnum()

    def test_generate_value_node_uri_number(self):
        """Test URI generation for numeric value."""
        result = generate_value_node_uri(123)
        assert len(result) == 32
        assert result.isalnum()

    def test_generate_value_node_uri_different_values(self):
        """Test that different values produce different URIs."""
        uri1 = generate_value_node_uri("test1")
        uri2 = generate_value_node_uri("test2")
        assert uri1 != uri2


class TestSerializeValue:
    def test_serialize_value_string(self):
        """Test serializing string value."""
        result = serialize_value("test string")
        assert result == "test string"

    def test_serialize_value_number(self):
        """Test serializing numeric value."""
        result = serialize_value(123.45)
        assert result == "123.45"

    def test_serialize_value_time_with_timezone_zero(self):
        """Test serializing time value with timezone 0 and leading +."""
        mock_time = MagicMock()
        mock_time.kind = "time"
        mock_time.value = "+2023-01-01T00:00:00Z"
        mock_time.timezone = 0
        mock_time.precision = 11
        mock_time.before = 0
        mock_time.after = 0
        mock_time.calendarmodel = "Q1985727"

        result = serialize_value(mock_time)
        expected = "t:2023-01-01T00:00:00Z:11:0:Q1985727"
        assert result == expected

    def test_serialize_value_time_with_bounds(self):
        """Test serializing time value with before/after bounds."""
        mock_time = MagicMock()
        mock_time.kind = "time"
        mock_time.value = "2023-01-01T00:00:00Z"
        mock_time.timezone = 0
        mock_time.precision = 11
        mock_time.before = -1
        mock_time.after = 1
        mock_time.calendarmodel = "Q1985727"

        result = serialize_value(mock_time)
        expected = "t:2023-01-01T00:00:00Z:11:0:-1:1:Q1985727"
        assert result == expected

    def test_serialize_value_quantity(self):
        """Test serializing quantity value."""
        mock_quantity = MagicMock()
        mock_quantity.kind = "quantity"
        mock_quantity.value = "123"
        mock_quantity.unit = "Q11573"
        mock_quantity.upper_bound = None
        mock_quantity.lower_bound = None

        result = serialize_value(mock_quantity)
        assert result == "q:123:Q11573"

    def test_serialize_value_quantity_with_bounds(self):
        """Test serializing quantity value with bounds."""
        mock_quantity = MagicMock()
        mock_quantity.kind = "quantity"
        mock_quantity.value = "123"
        mock_quantity.unit = "Q11573"
        mock_quantity.upper_bound = "124"
        mock_quantity.lower_bound = "122"

        result = serialize_value(mock_quantity)
        assert result == "q:123:Q11573:124:122"

    def test_serialize_value_globe(self):
        """Test serializing globe coordinate value."""
        mock_globe = MagicMock()
        mock_globe.kind = "globe"
        mock_globe.latitude = 51.5
        mock_globe.longitude = -0.1
        mock_globe.precision = 0.0001
        mock_globe.globe = "Q2"

        with patch(
            "models.rdf_builder.value_node._format_scientific_notation"
        ) as mock_format:
            mock_format.return_value = "1.0E-4"
            result = serialize_value(mock_globe)
            expected = "g:51.5:-0.1:1.0E-4:Q2"
            assert result == expected

    def test_serialize_value_no_kind(self):
        """Test serializing value without kind attribute."""
        result = serialize_value("simple string")
        assert result == "simple string"
