"""JSON entity schema value parser."""

from typing import Any

from models.internal_representation.json_fields import JsonField
from models.internal_representation.values.entity_schema_value import EntitySchemaValue


def parse_entity_schema_value(datavalue: dict[str, Any]) -> EntitySchemaValue:
    """Parse entity schema value from Wikidata JSON format."""
    return EntitySchemaValue(value=datavalue.get(JsonField.VALUE.value, ""))
