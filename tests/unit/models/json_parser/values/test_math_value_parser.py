"""Unit tests for math_value_parser."""

import pytest

from models.json_parser.values.math_value_parser import parse_math_value
from models.internal_representation.values.math_value import MathValue


class TestMathValueParser:
    """Unit tests for math value parser."""

    def test_parse_valid_math_value(self):
        """Test parsing a valid math value."""
        datavalue = {"value": "\\frac{a}{b} + \\sqrt{c}"}

        result = parse_math_value(datavalue)

        assert isinstance(result, MathValue)
        assert result.kind == "math"
        assert result.value == "\\frac{a}{b} + \\sqrt{c}"
        assert result.datatype_uri == "http://wikiba.se/ontology#Math"

    def test_parse_math_value_simple_expression(self):
        """Test parsing a simple mathematical expression."""
        datavalue = {"value": "E = mc^2"}

        result = parse_math_value(datavalue)

        assert result.value == "E = mc^2"

    def test_parse_math_value_complex_latex(self):
        """Test parsing a complex LaTeX mathematical expression."""
        datavalue = {
            "value": "\\int_{0}^{\\infty} e^{-x^2} \\, dx = \\frac{\\sqrt{\\pi}}{2}"
        }

        result = parse_math_value(datavalue)

        assert (
            result.value
            == "\\int_{0}^{\\infty} e^{-x^2} \\, dx = \\frac{\\sqrt{\\pi}}{2}"
        )

    def test_parse_math_value_empty_string(self):
        """Test parsing an empty math value."""
        datavalue = {"value": ""}

        result = parse_math_value(datavalue)

        assert result.value == ""

    def test_parse_math_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_math_value(datavalue)

        assert isinstance(result, MathValue)
        assert result.value == ""  # Empty string default

    def test_parse_math_value_unicode_symbols(self):
        """Test parsing a math value with unicode mathematical symbols."""
        datavalue = {"value": "∀x ∈ ℝ: x² ≥ 0"}

        result = parse_math_value(datavalue)

        assert result.value == "∀x ∈ ℝ: x² ≥ 0"

    def test_parse_math_value_mixed_content(self):
        """Test parsing a math value with mixed text and symbols."""
        datavalue = {"value": "Pythagorean theorem: a² + b² = c²"}

        result = parse_math_value(datavalue)

        assert result.value == "Pythagorean theorem: a² + b² = c²"

    def test_parse_math_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "x + y = z"}

        result = parse_math_value(datavalue)

        assert isinstance(result, MathValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_math_value_long_expression(self):
        """Test parsing a very long mathematical expression."""
        long_expression = (
            "\\frac{d}{dx} \\left[ \\int_{a}^{x} f(t) \\, dt \\right] = f(x)"
        )
        datavalue = {"value": long_expression}

        result = parse_math_value(datavalue)

        assert result.value == long_expression
