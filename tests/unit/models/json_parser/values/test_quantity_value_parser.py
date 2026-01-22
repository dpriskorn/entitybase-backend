"""Unit tests for quantity_value_parser."""

import pytest

from models.json_parser.values.quantity_value_parser import parse_quantity_value
from models.internal_representation.values.quantity_value import QuantityValue
from models.common import raise_validation_error


class TestQuantityValueParser:
    """Unit tests for quantity value parser."""

    def test_parse_valid_quantity_value(self):
        """Test parsing a valid quantity value."""
        datavalue = {
            "value": {
                "amount": "42.5",
                "unit": "http://www.wikidata.org/entity/Q11573",  # gram
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.kind == "quantity"
        assert result.value == "42.5"
        assert result.unit == "http://www.wikidata.org/entity/Q11573"
        assert result.upper_bound is None
        assert result.lower_bound is None
        assert result.datatype_uri == "http://wikiba.se/ontology#Quantity"

    def test_parse_quantity_with_bounds(self):
        """Test parsing a quantity value with upper and lower bounds."""
        datavalue = {
            "value": {
                "amount": "100",
                "unit": "1",
                "upperBound": "105",
                "lowerBound": "95"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "100"
        assert result.unit == "1"
        assert result.upper_bound == "105"
        assert result.lower_bound == "95"

    def test_parse_quantity_upper_bound_only(self):
        """Test parsing a quantity value with only upper bound."""
        datavalue = {
            "value": {
                "amount": "50",
                "unit": "http://www.wikidata.org/entity/Q712226",  # degree Celsius
                "upperBound": "52"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "50"
        assert result.upper_bound == "52"
        assert result.lower_bound is None

    def test_parse_quantity_lower_bound_only(self):
        """Test parsing a quantity value with only lower bound."""
        datavalue = {
            "value": {
                "amount": "10",
                "unit": "1",
                "lowerBound": "8"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "10"
        assert result.lower_bound == "8"
        assert result.upper_bound is None

    def test_parse_quantity_default_unit(self):
        """Test parsing a quantity value without unit (should default to '1')."""
        datavalue = {
            "value": {
                "amount": "25"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "25"
        assert result.unit == "1"  # Default unit

    def test_parse_quantity_zero_value(self):
        """Test parsing a quantity value of zero."""
        datavalue = {
            "value": {
                "amount": "0",
                "unit": "1"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "0"

    def test_parse_quantity_negative_value(self):
        """Test parsing a quantity value with negative amount."""
        datavalue = {
            "value": {
                "amount": "-15.5",
                "unit": "http://www.wikidata.org/entity/Q11579"  # kelvin
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "-15.5"

    def test_parse_quantity_scientific_notation(self):
        """Test parsing a quantity value in scientific notation."""
        datavalue = {
            "value": {
                "amount": "6.022e23",
                "unit": "1"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "6.022e23"

    def test_parse_quantity_missing_value_dict(self):
        """Test parsing when the value dict is missing."""
        datavalue = {}

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "0"  # Default when amount is missing
        assert result.unit == "1"   # Default unit

    def test_parse_quantity_missing_amount(self):
        """Test parsing when amount is missing from value dict."""
        datavalue = {
            "value": {
                "unit": "http://www.wikidata.org/entity/Q25343"  # meter
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.value == "0"  # Default when amount is missing

    def test_parse_quantity_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {
            "value": {
                "amount": "100",
                "unit": "1"
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_quantity_bounds_conversion_to_string(self):
        """Test that bounds are converted to strings."""
        datavalue = {
            "value": {
                "amount": "50",
                "unit": "1",
                "upperBound": 55,  # Numeric value
                "lowerBound": 45   # Numeric value
            }
        }

        result = parse_quantity_value(datavalue)

        assert isinstance(result, QuantityValue)
        assert result.upper_bound == "55"  # Converted to string
        assert result.lower_bound == "45"  # Converted to string
