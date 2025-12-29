from typing import Any

from services.shared.models.internal_representation.values import StringValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_string_value(datavalue: dict[str, Any]) -> StringValue:
    return StringValue(value=datavalue.get(JsonField.VALUE.value, ""))
