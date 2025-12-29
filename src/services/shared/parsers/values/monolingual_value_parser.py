from typing import Any

from services.shared.models.internal_representation.values import MonolingualValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_monolingual_value(datavalue: dict[str, Any]) -> MonolingualValue:
    mono_data = datavalue.get(JsonField.VALUE.value, {})
    return MonolingualValue(
        value="",
        language=mono_data.get(JsonField.LANGUAGE.value, ""),
        text=mono_data.get(JsonField.TEXT.value, ""),
    )
