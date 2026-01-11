"""JSON commons media value parser."""

from typing import Any

from models.internal_representation.values import CommonsMediaValue
from models.internal_representation.json_fields import JsonField


def parse_commons_media_value(datavalue: dict[str, Any]) -> CommonsMediaValue:
    """Parse commons media value from Wikidata JSON format."""
    return CommonsMediaValue(value=datavalue.get(JsonField.VALUE.value, ""))
