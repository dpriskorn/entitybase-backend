from typing import Any

from services.shared.models.internal_representation.values import URLValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_url_value(datavalue: dict[str, Any]) -> URLValue:
    return URLValue(value=datavalue.get(JsonField.VALUE.value, ""))
