from typing import Any

from services.shared.models.internal_representation.values import MathValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_math_value(datavalue: dict[str, Any]) -> MathValue:
    return MathValue(value=datavalue.get(JsonField.VALUE.value, ""))
