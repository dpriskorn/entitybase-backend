from typing import Any

from services.shared.models.internal_representation.values import GeoShapeValue
from services.shared.models.internal_representation.json_fields import JsonField


def parse_geo_shape_value(datavalue: dict[str, Any]) -> GeoShapeValue:
    return GeoShapeValue(value=datavalue.get(JsonField.VALUE.value, ""))
