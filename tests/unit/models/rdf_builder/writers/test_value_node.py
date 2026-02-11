"""Unit tests for value_node."""

import io
from unittest.mock import MagicMock

from models.rdf_builder.writers.value_node import (
    ValueNodeWriter,
    _format_scientific_notation,
)


class TestValueNode:
    """Unit tests for ValueNodeWriter."""

    def test_format_scientific_notation_no_leading_zero(self):
        """Test _format_scientific_notation removes leading zero in exponent."""
        result = _format_scientific_notation(1.0e-05)
        assert result == "1.0E-5"

        result = _format_scientific_notation(1.5e03)
        assert result == "1.5E+3"

    def test_format_scientific_notation_no_match(self):
        """Test _format_scientific_notation with no regex match."""
        result = _format_scientific_notation(1.0)
        assert result == "1.0E+0"

        result = _format_scientific_notation(123.456)
        assert result == "1.2E+2"

    def test_format_scientific_notation_various_values(self):
        """Test _format_scientific_notation with various values."""
        assert _format_scientific_notation(0.00001) == "1.0E-5"
        assert _format_scientific_notation(1000.0) == "1.0E+3"
        assert _format_scientific_notation(-0.001) == "-1.0E-3"
        assert _format_scientific_notation(1.234e-10) == "1.2E-10"

    def test_write_time_value_node_basic(self):
        """Test writing basic time value node."""
        output = io.StringIO()
        mock_time_value = MagicMock()
        mock_time_value.value = "+2023-12-25T00:00:00Z"
        mock_time_value.timezone = 0
        mock_time_value.precision = 11
        mock_time_value.calendarmodel = "http://www.wikidata.org/entity/Q1985727"

        ValueNodeWriter.write_time_value_node(output, "time123", mock_time_value)

        result = output.getvalue()
        assert "wdv:time123 a wikibase:TimeValue ;" in result
        assert '"2023-12-25T00:00:00Z"^^xsd:dateTime' in result  # Leading + removed
        assert '"11"^^xsd:integer' in result
        assert '"0"^^xsd:integer' in result
        assert "http://www.wikidata.org/entity/Q1985727" in result

    def test_write_time_value_node_with_dedupe_skip(self):
        """Test time value node writing with deduplication skip."""
        output = io.StringIO()
        mock_time_value = MagicMock()
        mock_dedupe = MagicMock()
        mock_dedupe.already_seen.return_value = True

        ValueNodeWriter.write_time_value_node(
            output, "time123", mock_time_value, mock_dedupe
        )

        mock_dedupe.already_seen.assert_called_once_with("time123", "wdv")
        assert output.getvalue() == ""  # Nothing written

    def test_write_time_value_node_with_dedupe_write(self):
        """Test time value node writing with deduplication allow."""
        output = io.StringIO()
        mock_time_value = MagicMock()
        mock_time_value.value = "+2023-12-25T00:00:00Z"
        mock_time_value.timezone = 0
        mock_time_value.precision = 11
        mock_time_value.calendarmodel = "http://www.wikidata.org/entity/Q1985727"
        mock_dedupe = MagicMock()
        mock_dedupe.already_seen.return_value = False

        ValueNodeWriter.write_time_value_node(
            output, "time123", mock_time_value, mock_dedupe
        )

        mock_dedupe.already_seen.assert_called_once_with("time123", "wdv")
        assert "wdv:time123" in output.getvalue()

    def test_write_quantity_value_node_basic(self):
        """Test writing basic quantity value node."""
        output = io.StringIO()
        mock_quantity_value = MagicMock()
        mock_quantity_value.value = "42.5"
        mock_quantity_value.unit = "http://www.wikidata.org/entity/Q11573"
        mock_quantity_value.upper_bound = None
        mock_quantity_value.lower_bound = None

        ValueNodeWriter.write_quantity_value_node(
            output, "quantity123", mock_quantity_value
        )

        result = output.getvalue()
        assert "wdv:quantity123 a wikibase:QuantityValue ;" in result
        assert '"42.5"^^xsd:decimal' in result
        assert "http://www.wikidata.org/entity/Q11573" in result
        assert result.endswith(" .\n")

    def test_write_quantity_value_node_with_upper_bound(self):
        """Test writing quantity value node with upper bound."""
        output = io.StringIO()
        mock_quantity_value = MagicMock()
        mock_quantity_value.value = "42.5"
        mock_quantity_value.unit = "http://www.wikidata.org/entity/Q11573"
        mock_quantity_value.upper_bound = "50.0"
        mock_quantity_value.lower_bound = None

        ValueNodeWriter.write_quantity_value_node(
            output, "quantity123", mock_quantity_value
        )

        result = output.getvalue()
        assert '"42.5"^^xsd:decimal' in result
        assert '"50.0"^^xsd:decimal' in result
        assert "quantityUpperBound" in result
        assert "quantityLowerBound" not in result

    def test_write_quantity_value_node_with_lower_bound(self):
        """Test writing quantity value node with lower bound."""
        output = io.StringIO()
        mock_quantity_value = MagicMock()
        mock_quantity_value.value = "42.5"
        mock_quantity_value.unit = "http://www.wikidata.org/entity/Q11573"
        mock_quantity_value.upper_bound = None
        mock_quantity_value.lower_bound = "35.0"

        ValueNodeWriter.write_quantity_value_node(
            output, "quantity123", mock_quantity_value
        )

        result = output.getvalue()
        assert '"42.5"^^xsd:decimal' in result
        assert '"35.0"^^xsd:decimal' in result
        assert "quantityLowerBound" in result
        assert "quantityUpperBound" not in result

    def test_write_quantity_value_node_with_both_bounds(self):
        """Test writing quantity value node with both bounds."""
        output = io.StringIO()
        mock_quantity_value = MagicMock()
        mock_quantity_value.value = "42.5"
        mock_quantity_value.unit = "http://www.wikidata.org/entity/Q11573"
        mock_quantity_value.upper_bound = "50.0"
        mock_quantity_value.lower_bound = "35.0"

        ValueNodeWriter.write_quantity_value_node(
            output, "quantity123", mock_quantity_value
        )

        result = output.getvalue()
        assert '"42.5"^^xsd:decimal' in result
        assert '"50.0"^^xsd:decimal' in result
        assert '"35.0"^^xsd:decimal' in result
        assert "quantityUpperBound" in result
        assert "quantityLowerBound" in result

    def test_write_quantity_value_node_with_dedupe_skip(self):
        """Test quantity value node writing with deduplication skip."""
        output = io.StringIO()
        mock_quantity_value = MagicMock()
        mock_dedupe = MagicMock()
        mock_dedupe.already_seen.return_value = True

        ValueNodeWriter.write_quantity_value_node(
            output, "quantity123", mock_quantity_value, mock_dedupe
        )

        mock_dedupe.already_seen.assert_called_once_with("quantity123", "wdv")
        assert output.getvalue() == ""

    def test_write_globe_value_node_basic(self):
        """Test writing basic globe coordinate value node."""
        output = io.StringIO()
        mock_globe_value = MagicMock()
        mock_globe_value.latitude = 40.7128
        mock_globe_value.longitude = -74.0060
        mock_globe_value.precision = 0.0001
        mock_globe_value.globe = "http://www.wikidata.org/entity/Q2"

        ValueNodeWriter.write_globe_value_node(output, "globe123", mock_globe_value)

        result = output.getvalue()
        assert "wdv:globe123 a wikibase:GlobecoordinateValue ;" in result
        assert '"40.7128"^^xsd:double' in result
        assert '"-74.006"^^xsd:double' in result
        assert '"1.0E-4"^^xsd:double' in result  # Formatted precision
        assert "http://www.wikidata.org/entity/Q2" in result

    def test_write_globe_value_node_with_dedupe_skip(self):
        """Test globe value node writing with deduplication skip."""
        output = io.StringIO()
        mock_globe_value = MagicMock()
        mock_dedupe = MagicMock()
        mock_dedupe.already_seen.return_value = True

        ValueNodeWriter.write_globe_value_node(
            output, "globe123", mock_globe_value, mock_dedupe
        )

        mock_dedupe.already_seen.assert_called_once_with("globe123", "wdv")
        assert output.getvalue() == ""

    def test_write_globe_value_node_precision_formatting(self):
        """Test globe value node with various precision values."""
        output = io.StringIO()
        mock_globe_value = MagicMock()
        mock_globe_value.latitude = 0.0
        mock_globe_value.longitude = 0.0
        mock_globe_value.globe = "http://www.wikidata.org/entity/Q2"

        # Test small precision
        mock_globe_value.precision = 1e-6
        ValueNodeWriter.write_globe_value_node(output, "globe123", mock_globe_value)

        result = output.getvalue()
        assert '"1.0E-6"^^xsd:double' in result

    def test_write_time_value_node_no_dedupe(self):
        """Test time value node writing without deduplication."""
        output = io.StringIO()
        mock_time_value = MagicMock()
        mock_time_value.value = "+2023-12-25T00:00:00Z"
        mock_time_value.timezone = 0
        mock_time_value.precision = 11
        mock_time_value.calendarmodel = "http://www.wikidata.org/entity/Q1985727"

        ValueNodeWriter.write_time_value_node(output, "time123", mock_time_value, None)

        assert "wdv:time123" in output.getvalue()

    def test_write_quantity_value_node_no_dedupe(self):
        """Test quantity value node writing without deduplication."""
        output = io.StringIO()
        mock_quantity_value = MagicMock()
        mock_quantity_value.value = "42.5"
        mock_quantity_value.unit = "http://www.wikidata.org/entity/Q11573"
        mock_quantity_value.upper_bound = None
        mock_quantity_value.lower_bound = None

        ValueNodeWriter.write_quantity_value_node(
            output, "quantity123", mock_quantity_value, None
        )

        assert "wdv:quantity123" in output.getvalue()

    def test_write_globe_value_node_no_dedupe(self):
        """Test globe value node writing without deduplication."""
        output = io.StringIO()
        mock_globe_value = MagicMock()
        mock_globe_value.latitude = 40.7128
        mock_globe_value.longitude = -74.0060
        mock_globe_value.precision = 0.0001
        mock_globe_value.globe = "http://www.wikidata.org/entity/Q2"

        ValueNodeWriter.write_globe_value_node(
            output, "globe123", mock_globe_value, None
        )

        assert "wdv:globe123" in output.getvalue()
