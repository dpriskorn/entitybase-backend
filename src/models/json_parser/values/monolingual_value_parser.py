"""JSON monolingual value parser."""

from typing import Any

from models.internal_representation.values import MonolingualValue
from models.internal_representation.json_fields import JsonField


def parse_monolingual_value(datavalue: dict[str, Any]) -> MonolingualValue:
    """Parse monolingual value from Wikidata JSON format."""
    mono_data = datavalue.get(JsonField.VALUE.value, {})
    return MonolingualValue(
        value="",
        language=mono_data.get(JsonField.LANGUAGE.value, ""),
        text=mono_data.get(JsonField.TEXT.value, ""),
    )
