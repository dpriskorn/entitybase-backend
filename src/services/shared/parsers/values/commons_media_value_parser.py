from typing import Any

from services.shared.models.internal_representation.values import CommonsMediaValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_commons_media_value(datavalue: dict[str, Any]) -> CommonsMediaValue:
    return CommonsMediaValue(value=datavalue.get(JsonField.VALUE.value, ""))
