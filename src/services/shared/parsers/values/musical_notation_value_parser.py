from typing import Any

from services.shared.models.internal_representation.values import MusicalNotationValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_musical_notation_value(datavalue: dict[str, Any]) -> MusicalNotationValue:
    return MusicalNotationValue(value=datavalue.get(JsonField.VALUE.value, ""))
