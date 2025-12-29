from typing import Any

from services.shared.models.internal_representation.values import ExternalIDValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_external_id_value(datavalue: dict[str, Any]) -> ExternalIDValue:
    return ExternalIDValue(value=datavalue.get(JsonField.VALUE.value, ""))
