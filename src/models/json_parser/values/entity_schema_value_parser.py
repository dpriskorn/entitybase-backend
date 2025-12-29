from typing import Any

from models.internal_representation.values import EntitySchemaValue
from models.internal_representation.json_fields import JsonField


def parse_entity_schema_value(datavalue: dict[str, Any]) -> EntitySchemaValue:
    return EntitySchemaValue(value=datavalue.get(JsonField.VALUE.value, ""))
