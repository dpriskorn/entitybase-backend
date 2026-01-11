"""JSON globe value parser."""

from typing import Any

from models.internal_representation.values import GlobeValue
from models.internal_representation.json_fields import JsonField


def parse_globe_value(datavalue: dict[str, Any]) -> GlobeValue:
    """Parse globe value from Wikidata JSON format."""
    globe_data = datavalue.get(JsonField.VALUE.value, {})
    altitude = globe_data.get(JsonField.ALTITUDE.value)
    return GlobeValue(
        value="",
        latitude=float(globe_data.get(JsonField.LATITUDE.value, 0.0)),
        longitude=float(globe_data.get(JsonField.LONGITUDE.value, 0.0)),
        altitude=float(altitude) if altitude is not None else None,
        precision=float(globe_data.get(JsonField.PRECISION.value, 1 / 3600)),
        globe=globe_data.get(
            JsonField.GLOBE.value, "http://www.wikidata.org/entity/Q2"
        ),
    )
