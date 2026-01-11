"""JSON time value parser."""

from typing import Any

from models.internal_representation.values import TimeValue
from models.internal_representation.json_fields import JsonField


def parse_time_value(datavalue: dict[str, Any]) -> TimeValue:
    """Parse time value from Wikidata JSON format."""
    time_data = datavalue.get(JsonField.VALUE.value, {})
    return TimeValue(
        value=time_data.get(JsonField.TIME.value, ""),
        timezone=time_data.get(JsonField.TIMEZONE.value, 0),
        before=time_data.get(JsonField.BEFORE.value, 0),
        after=time_data.get(JsonField.AFTER.value, 0),
        precision=time_data.get(JsonField.PRECISION.value, 11),
        calendarmodel=time_data.get(
            JsonField.CALENDARMODEL.value, "http://www.wikidata.org/entity/Q1985727"
        ),
    )
