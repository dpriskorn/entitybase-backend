"""Unit tests for external_id_value_parser."""

import pytest

from models.json_parser.values.external_id_value_parser import parse_external_id_value
from models.internal_representation.values.external_id_value import ExternalIDValue


class TestExternalIdValueParser:
    """Unit tests for external ID value parser."""

    def test_parse_valid_external_id_value(self):
        """Test parsing a valid external ID value."""
        datavalue = {"value": "ISBN 978-0-123456-78-9"}

        result = parse_external_id_value(datavalue)

        assert isinstance(result, ExternalIDValue)
        assert result.kind == "external_id"
        assert result.value == "ISBN 978-0-123456-78-9"
        assert result.datatype_uri == "http://wikiba.se/ontology#ExternalId"

    def test_parse_external_id_value_numeric(self):
        """Test parsing an external ID value that is numeric."""
        datavalue = {"value": "123456789"}

        result = parse_external_id_value(datavalue)

        assert result.value == "123456789"

    def test_parse_external_id_value_empty_string(self):
        """Test parsing an external ID value that is an empty string."""
        datavalue = {"value": ""}

        result = parse_external_id_value(datavalue)

        assert result.value == ""

    def test_parse_external_id_value_special_characters(self):
        """Test parsing an external ID value with special characters."""
        datavalue = {"value": "DOI:10.1000/xyz123"}

        result = parse_external_id_value(datavalue)

        assert result.value == "DOI:10.1000/xyz123"

    def test_parse_external_id_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_external_id_value(datavalue)

        assert isinstance(result, ExternalIDValue)
        assert result.value == ""  # Empty string default

    def test_parse_external_id_value_unicode(self):
        """Test parsing an external ID value with unicode characters."""
        datavalue = {"value": "测试_ID_123"}

        result = parse_external_id_value(datavalue)

        assert result.value == "测试_ID_123"

    def test_parse_external_id_value_long_string(self):
        """Test parsing a very long external ID value."""
        long_id = "A" * 1000  # Very long string
        datavalue = {"value": long_id}

        result = parse_external_id_value(datavalue)

        assert result.value == long_id

    def test_parse_external_id_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "ISBN 123456789"}

        result = parse_external_id_value(datavalue)

        assert isinstance(result, ExternalIDValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_external_id_value_whitespace(self):
        """Test parsing an external ID value with whitespace."""
        datavalue = {"value": "  spaced out  "}

        result = parse_external_id_value(datavalue)

        assert result.value == "  spaced out  "  # Whitespace preserved
