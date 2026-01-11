"""JSON string value parser."""

from typing import Any

from models.internal_representation.values import StringValue
from models.internal_representation.json_fields import JsonField


def parse_string_value(datavalue: dict[str, Any]) -> StringValue:
    """Parse string value from Wikidata JSON format."""
    return StringValue(value=datavalue.get(JsonField.VALUE.value, ""))
