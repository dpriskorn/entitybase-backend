"""Unit tests for novalue_value_parser."""

import pytest

from models.json_parser.values.novalue_value_parser import parse_novalue_value
from models.internal_representation.values.novalue_value import NoValue


class TestNovalueValueParser:
    """Unit tests for novalue value parser."""

    def test_parse_novalue_value(self):
        """Test parsing a novalue value."""
        result = parse_novalue_value()

        assert isinstance(result, NoValue)
        assert result.kind == "novalue"
        assert result.value is None
        assert result.datatype_uri == "http://wikiba.se/ontology#NoValue"

    def test_parse_novalue_value_multiple_calls(self):
        """Test that multiple calls return equivalent NoValue instances."""
        result1 = parse_novalue_value()
        result2 = parse_novalue_value()

        assert isinstance(result1, NoValue)
        assert isinstance(result2, NoValue)
        assert result1.kind == result2.kind
        assert result1.value == result2.value
        assert result1.datatype_uri == result2.datatype_uri

    def test_parse_novalue_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        result = parse_novalue_value()

        assert isinstance(result, NoValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            # noinspection PyTypeChecker
            result.value = "modified"

    def test_parse_novalue_value_idempotent(self):
        """Test that parsing is idempotent - same result every time."""
        # Call multiple times and ensure identical results
        results = [parse_novalue_value() for _ in range(5)]

        for result in results:
            assert isinstance(result, NoValue)
            assert result.kind == "novalue"
            assert result.value is None
            assert result.datatype_uri == "http://wikiba.se/ontology#NoValue"