"""JSON quantity value parser."""

from typing import Any

from models.internal_representation.values import QuantityValue
from models.internal_representation.json_fields import JsonField


def parse_quantity_value(datavalue: dict[str, Any]) -> QuantityValue:
    """Parse quantity value from Wikidata JSON format."""
    quantity_data = datavalue.get(JsonField.VALUE.value, {})
    return QuantityValue(
        value=str(quantity_data.get(JsonField.AMOUNT.value, "0")),
        unit=quantity_data.get(JsonField.UNIT.value, "1"),
        upper_bound=(
            str(quantity_data[JsonField.UPPER_BOUND.value])
            if JsonField.UPPER_BOUND.value in quantity_data
            else None
        ),
        lower_bound=(
            str(quantity_data[JsonField.LOWER_BOUND.value])
            if JsonField.LOWER_BOUND.value in quantity_data
            else None
        ),
    )
