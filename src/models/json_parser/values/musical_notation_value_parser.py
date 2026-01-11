"""JSON musical notation value parser."""

from typing import Any

from models.internal_representation.values.musical_notation_value import (
    MusicalNotationValue,
)
from models.internal_representation.json_fields import JsonField


def parse_musical_notation_value(datavalue: dict[str, Any]) -> MusicalNotationValue:
    """Parse musical notation value from Wikidata JSON format."""
    return MusicalNotationValue(value=datavalue.get(JsonField.VALUE.value, ""))
