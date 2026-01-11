"""JSON external ID value parser."""

from typing import Any

from models.internal_representation.values import ExternalIDValue
from models.internal_representation.json_fields import JsonField


def parse_external_id_value(datavalue: dict[str, Any]) -> ExternalIDValue:
    """Parse external ID value from Wikidata JSON format."""
    return ExternalIDValue(value=datavalue.get(JsonField.VALUE.value, ""))
