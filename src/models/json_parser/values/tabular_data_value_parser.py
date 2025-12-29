from typing import Any

from models.internal_representation.values import TabularDataValue
from models.internal_representation.json_fields import JsonField


def parse_tabular_data_value(datavalue: dict[str, Any]) -> TabularDataValue:
    return TabularDataValue(value=datavalue.get(JsonField.VALUE.value, ""))
