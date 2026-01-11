"""JSON math value parser."""

from typing import Any

from models.internal_representation.values.math_value import MathValue
from models.internal_representation.json_fields import JsonField


def parse_math_value(datavalue: dict[str, Any]) -> MathValue:
    """Parse math value from Wikidata JSON format."""
    return MathValue(value=datavalue.get(JsonField.VALUE.value, ""))
