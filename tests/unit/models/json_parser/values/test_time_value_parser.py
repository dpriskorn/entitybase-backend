"""Unit tests for time_value_parser."""

import pytest

from models.internal_representation.values.time_value import TimeValue
from models.json_parser.values.time_value_parser import parse_time_value


class TestTimeValueParser:
    """Unit tests for time value parser."""

    def test_parse_valid_time_value(self):
        """Test parsing a valid time value."""
        datavalue = {
            "value": {
                "time": "+2023-12-25T00:00:00Z",
                "timezone": 60,
                "before": 1,
                "after": 2,
                "precision": 11,
                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
            }
        }

        result = parse_time_value(datavalue)

        assert isinstance(result, TimeValue)
        assert result.kind == "time"
        assert result.value == "+2023-12-25T00:00:00Z"
        assert result.timezone == 60
        assert result.before == 1
        assert result.after == 2
        assert result.precision == 11
        assert result.calendarmodel == "http://www.wikidata.org/entity/Q1985727"
        assert result.datatype_uri == "http://wikiba.se/ontology#Time"

    def test_parse_time_value_defaults(self):
        """Test parsing time value with minimal data (all defaults)."""
        datavalue = {"value": {"time": "+2023-12-25T00:00:00Z"}}

        result = parse_time_value(datavalue)

        assert isinstance(result, TimeValue)
        assert result.value == "+2023-12-25T00:00:00Z"
        assert result.timezone == 0  # Default
        assert result.before == 0  # Default
        assert result.after == 0  # Default
        assert result.precision == 11  # Default
        assert (
            result.calendarmodel == "http://www.wikidata.org/entity/Q1985727"
        )  # Default

    def test_parse_time_value_missing_timezone(self):
        """Test parsing time value without timezone."""
        datavalue = {
            "value": {
                "time": "+2023-12-25T00:00:00Z",
                "before": 5,
                "after": 3,
                "precision": 10,
            }
        }

        result = parse_time_value(datavalue)

        assert result.timezone == 0
        assert result.before == 5
        assert result.after == 3
        assert result.precision == 10

    def test_parse_time_value_negative_timezone(self):
        """Test parsing time value with negative timezone."""
        datavalue = {
            "value": {
                "time": "+2023-12-25T00:00:00Z",
                "timezone": -300,  # UTC-5
            }
        }

        result = parse_time_value(datavalue)

        assert result.timezone == -300

    def test_parse_time_value_custom_calendar_model(self):
        """Test parsing time value with custom calendar model."""
        datavalue = {
            "value": {
                "time": "+2023-12-25T00:00:00Z",
                "calendarmodel": "http://www.wikidata.org/entity/Q1985786",  # Julian calendar
            }
        }

        result = parse_time_value(datavalue)

        assert result.calendarmodel == "http://www.wikidata.org/entity/Q1985786"

    def test_parse_time_value_qid_calendar_model(self):
        """Test parsing time value with QID-only calendar model (gets normalized)."""
        datavalue = {
            "value": {"time": "+2023-12-25T00:00:00Z", "calendarmodel": "Q1985786"}
        }

        result = parse_time_value(datavalue)

        assert result.calendarmodel == "http://www.wikidata.org/entity/Q1985786"

    def test_parse_time_value_precision_zero(self):
        """Test parsing time value with precision 0."""
        datavalue = {"value": {"time": "+2023-12-25T00:00:00Z", "precision": 0}}

        result = parse_time_value(datavalue)

        assert result.precision == 0

    def test_parse_time_value_precision_max(self):
        """Test parsing time value with maximum precision 14."""
        datavalue = {"value": {"time": "+2023-12-25T00:00:00Z", "precision": 14}}

        result = parse_time_value(datavalue)
        assert result.precision == 14

    def test_parse_time_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": {"time": "+2023-12-25T00:00:00Z", "timezone": 60}}

        result = parse_time_value(datavalue)

        assert isinstance(result, TimeValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_time_value_adds_plus_prefix(self):
        """Test that time value without + prefix gets it added automatically."""
        datavalue = {
            "value": {
                "time": "2023-12-25T00:00:00Z"  # Missing +
            }
        }

        result = parse_time_value(datavalue)

        assert result.value == "+2023-12-25T00:00:00Z"  # + added

    def test_parse_time_value_negative_year(self):
        """Test parsing time value with negative year."""
        datavalue = {"value": {"time": "-0045-03-15T00:00:00Z"}}

        result = parse_time_value(datavalue)

        assert result.value == "-0045-03-15T00:00:00Z"

    def test_parse_time_value_already_has_plus(self):
        """Test that time value already with + prefix is unchanged."""
        datavalue = {"value": {"time": "+2023-12-25T00:00:00Z"}}

        result = parse_time_value(datavalue)

        assert result.value == "+2023-12-25T00:00:00Z"
