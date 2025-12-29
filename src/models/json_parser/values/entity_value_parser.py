from typing import Any

from models.internal_representation.values import EntityValue
from models.internal_representation.json_fields import JsonField


def parse_entity_value(datavalue: dict[str, Any]) -> EntityValue:
    entity_id = datavalue.get(JsonField.VALUE.value, {}).get(JsonField.ID.value, "")
    return EntityValue(value=entity_id)
