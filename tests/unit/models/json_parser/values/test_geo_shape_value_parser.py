"""Unit tests for geo_shape_value_parser."""

import pytest

from models.json_parser.values.geo_shape_value_parser import parse_geo_shape_value
from models.internal_representation.values.geo_shape_value import GeoShapeValue


class TestGeoShapeValueParser:
    """Unit tests for geo shape value parser."""

    def test_parse_valid_geo_shape_value(self):
        """Test parsing a valid geo shape value."""
        datavalue = {"value": "Data:World_Map.svg"}

        result = parse_geo_shape_value(datavalue)

        assert isinstance(result, GeoShapeValue)
        assert result.kind == "geo_shape"
        assert result.value == "Data:World_Map.svg"
        assert result.datatype_uri == "http://wikiba.se/ontology#GeoShape"

    def test_parse_geo_shape_value_wikidata_file(self):
        """Test parsing a geo shape value referencing a Wikidata file."""
        datavalue = {"value": "Data:Europe.svg"}

        result = parse_geo_shape_value(datavalue)

        assert result.value == "Data:Europe.svg"

    def test_parse_geo_shape_value_complex_filename(self):
        """Test parsing a geo shape value with complex filename."""
        datavalue = {"value": "Data:United_States_outline_with_state_boundaries.svg"}

        result = parse_geo_shape_value(datavalue)

        assert result.value == "Data:United_States_outline_with_state_boundaries.svg"

    def test_parse_geo_shape_value_empty_string(self):
        """Test parsing an empty geo shape value."""
        datavalue = {"value": ""}

        result = parse_geo_shape_value(datavalue)

        assert result.value == ""

    def test_parse_geo_shape_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_geo_shape_value(datavalue)

        assert isinstance(result, GeoShapeValue)
        assert result.value == ""  # Empty string default

    def test_parse_geo_shape_value_different_formats(self):
        """Test parsing geo shape values in different formats."""
        formats = [
            "Data:map.kml",
            "Data:region.geojson",
            "Data:boundary.topojson",
            "Data:shape.wkt",
        ]

        for fmt in formats:
            datavalue = {"value": fmt}
            result = parse_geo_shape_value(datavalue)
            assert result.value == fmt

    def test_parse_geo_shape_value_unicode_filename(self):
        """Test parsing a geo shape value with unicode characters."""
        datavalue = {"value": "Data:Карта_мира.svg"}

        result = parse_geo_shape_value(datavalue)

        assert result.value == "Data:Карта_мира.svg"

    def test_parse_geo_shape_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "Data:World.svg"}

        result = parse_geo_shape_value(datavalue)

        assert isinstance(result, GeoShapeValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_geo_shape_value_long_filename(self):
        """Test parsing a geo shape value with a very long filename."""
        long_filename = "Data:" + "A" * 200 + ".svg"
        datavalue = {"value": long_filename}

        result = parse_geo_shape_value(datavalue)

        assert result.value == long_filename
