"""Unit tests for globe_value_parser."""

import pytest

from models.json_parser.values.globe_value_parser import parse_globe_value
from models.internal_representation.values.globe_value import GlobeValue


class TestGlobeValueParser:
    """Unit tests for globe value parser."""

    def test_parse_valid_globe_value(self):
        """Test parsing a valid globe value."""
        datavalue = {
            "value": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "altitude": 10.0,
                "precision": 0.0001,
                "globe": "http://www.wikidata.org/entity/Q2",
            }
        }

        result = parse_globe_value(datavalue)

        assert isinstance(result, GlobeValue)
        assert result.kind == "globe"
        assert result.value == ""  # Always empty string
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.altitude == 10.0
        assert result.precision == 0.0001
        assert result.globe == "http://www.wikidata.org/entity/Q2"
        assert result.datatype_uri == "http://wikiba.se/ontology#GlobeCoordinate"

    def test_parse_globe_value_defaults(self):
        """Test parsing globe value with minimal data (all defaults)."""
        datavalue = {"value": {"latitude": 51.5074, "longitude": -0.1278}}

        result = parse_globe_value(datavalue)

        assert result.latitude == 51.5074
        assert result.longitude == -0.1278
        assert result.altitude is None  # Default
        assert result.precision == 1 / 3600  # Default precision
        assert result.globe == "http://www.wikidata.org/entity/Q2"  # Default Earth

    def test_parse_globe_value_qid_globe(self):
        """Test parsing globe value with QID globe (gets normalized)."""
        datavalue = {"value": {"latitude": 0.0, "longitude": 0.0, "globe": "Q405"}}

        result = parse_globe_value(datavalue)

        assert result.globe == "http://www.wikidata.org/entity/Q405"

    def test_parse_globe_value_full_url_globe(self):
        """Test parsing globe value with full URL globe."""
        datavalue = {
            "value": {
                "latitude": 0.0,
                "longitude": 0.0,
                "globe": "http://www.wikidata.org/entity/Q111",
            }
        }

        result = parse_globe_value(datavalue)

        assert result.globe == "http://www.wikidata.org/entity/Q111"

    def test_parse_globe_value_negative_coordinates(self):
        """Test parsing globe value with negative coordinates."""
        datavalue = {"value": {"latitude": -33.8688, "longitude": -151.2093}}

        result = parse_globe_value(datavalue)

        assert result.latitude == -33.8688
        assert result.longitude == -151.2093

    def test_parse_globe_value_zero_coordinates(self):
        """Test parsing globe value with zero coordinates."""
        datavalue = {"value": {"latitude": 0.0, "longitude": 0.0}}

        result = parse_globe_value(datavalue)

        assert result.latitude == 0.0
        assert result.longitude == 0.0

    def test_parse_globe_value_boundary_latitude(self):
        """Test parsing globe value with boundary latitude values."""
        # Test north pole
        datavalue_north = {"value": {"latitude": 90.0, "longitude": 0.0}}
        result_north = parse_globe_value(datavalue_north)
        assert result_north.latitude == 90.0

        # Test south pole
        datavalue_south = {"value": {"latitude": -90.0, "longitude": 0.0}}
        result_south = parse_globe_value(datavalue_south)
        assert result_south.latitude == -90.0

    def test_parse_globe_value_boundary_longitude(self):
        """Test parsing globe value with boundary longitude values."""
        # Test positive boundary
        datavalue_east = {"value": {"latitude": 0.0, "longitude": 180.0}}
        result_east = parse_globe_value(datavalue_east)
        assert result_east.longitude == 180.0

        # Test negative boundary
        datavalue_west = {"value": {"latitude": 0.0, "longitude": -180.0}}
        result_west = parse_globe_value(datavalue_west)
        assert result_west.longitude == -180.0

    def test_parse_globe_value_missing_value_dict(self):
        """Test parsing when the value dict is missing."""
        datavalue = {}

        result = parse_globe_value(datavalue)

        assert isinstance(result, GlobeValue)
        assert result.latitude == 0.0  # Default
        assert result.longitude == 0.0  # Default
        assert result.altitude is None
        assert result.precision == 1 / 3600
        assert result.globe == "http://www.wikidata.org/entity/Q2"

    def test_parse_globe_value_missing_latitude(self):
        """Test parsing when latitude is missing."""
        datavalue = {"value": {"longitude": 45.0}}

        result = parse_globe_value(datavalue)

        assert result.latitude == 0.0  # Default
        assert result.longitude == 45.0

    def test_parse_globe_value_missing_longitude(self):
        """Test parsing when longitude is missing."""
        datavalue = {"value": {"latitude": 30.0}}

        result = parse_globe_value(datavalue)

        assert result.latitude == 30.0
        assert result.longitude == 0.0  # Default

    def test_parse_globe_value_zero_altitude(self):
        """Test parsing globe value with zero altitude."""
        datavalue = {"value": {"latitude": 40.0, "longitude": -75.0, "altitude": 0.0}}

        result = parse_globe_value(datavalue)

        assert result.altitude == 0.0

    def test_parse_globe_value_negative_altitude(self):
        """Test parsing globe value with negative altitude."""
        datavalue = {
            "value": {"latitude": 40.0, "longitude": -75.0, "altitude": -100.0}
        }

        result = parse_globe_value(datavalue)

        assert result.altitude == -100.0

    def test_parse_globe_value_high_precision(self):
        """Test parsing globe value with very high precision."""
        datavalue = {
            "value": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "precision": 0.0000001,
            }
        }

        result = parse_globe_value(datavalue)

        assert result.precision == 0.0000001

    def test_parse_globe_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": {"latitude": 40.0, "longitude": -75.0}}

        result = parse_globe_value(datavalue)

        assert isinstance(result, GlobeValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.latitude = 50.0
