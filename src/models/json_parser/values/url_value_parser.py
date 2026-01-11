"""JSON URL value parser."""

from typing import Any

from models.internal_representation.values import URLValue
from models.internal_representation.json_fields import JsonField


def parse_url_value(datavalue: dict[str, Any]) -> URLValue:
    """Parse URL value from Wikidata JSON format."""
    return URLValue(value=datavalue.get(JsonField.VALUE.value, ""))
