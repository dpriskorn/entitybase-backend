"""JSON string value parser."""

from typing import Any

from models.internal_representation.values import StringValue
from models.internal_representation.json_fields import JsonField


def parse_string_value(datavalue: dict[str, Any]) -> StringValue:
    """Parse string value from Wikidata JSON format."""
    value = datavalue.get(JsonField.VALUE.value, "")
    # Convert to string if it's not already a string
    if value is None:
        value = ""
    else:
        value = str(value)
    return StringValue(value=value)
