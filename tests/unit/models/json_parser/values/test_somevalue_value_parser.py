"""Unit tests for somevalue_value_parser."""

import pytest

from models.json_parser.values.somevalue_value_parser import parse_somevalue_value
from models.internal_representation.values.somevalue_value import SomeValue


class TestSomevalueValueParser:
    """Unit tests for somevalue value parser."""

    def test_parse_somevalue_value(self):
        """Test parsing a somevalue value."""
        result = parse_somevalue_value()

        assert isinstance(result, SomeValue)
        assert result.kind == "somevalue"
        assert result.value is None
        assert result.datatype_uri == "http://wikiba.se/ontology#SomeValue"

    def test_parse_somevalue_value_multiple_calls(self):
        """Test that multiple calls return equivalent SomeValue instances."""
        result1 = parse_somevalue_value()
        result2 = parse_somevalue_value()

        assert isinstance(result1, SomeValue)
        assert isinstance(result2, SomeValue)
        assert result1.kind == result2.kind
        assert result1.value == result2.value
        assert result1.datatype_uri == result2.datatype_uri

    def test_parse_somevalue_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        result = parse_somevalue_value()

        assert isinstance(result, SomeValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            # noinspection PyTypeChecker
            result.value = "modified"

    def test_parse_somevalue_value_idempotent(self):
        """Test that parsing is idempotent - same result every time."""
        # Call multiple times and ensure identical results
        results = [parse_somevalue_value() for _ in range(5)]

        for result in results:
            assert isinstance(result, SomeValue)
            assert result.kind == "somevalue"
            assert result.value is None
            assert result.datatype_uri == "http://wikiba.se/ontology#SomeValue"