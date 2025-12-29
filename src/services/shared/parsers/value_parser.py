from typing import Any

from .values.entity_value_parser import parse_entity_value
from .values.string_value_parser import parse_string_value
from .values.time_value_parser import parse_time_value
from .values.quantity_value_parser import parse_quantity_value
from .values.globe_value_parser import parse_globe_value
from .values.monolingual_value_parser import parse_monolingual_value
from .values.external_id_value_parser import parse_external_id_value
from .values.commons_media_value_parser import parse_commons_media_value
from .values.geo_shape_value_parser import parse_geo_shape_value
from .values.tabular_data_value_parser import parse_tabular_data_value
from .values.musical_notation_value_parser import parse_musical_notation_value
from .values.url_value_parser import parse_url_value
from .values.math_value_parser import parse_math_value
from .values.entity_schema_value_parser import parse_entity_schema_value
from services.shared.models.internal_representation.datatypes import Datatype
from services.shared.models.internal_representation.json_fields import JsonField


def parse_value(snak_json: dict[str, Any]):
    if snak_json.get(JsonField.SNAKTYPE.value) != JsonField.VALUE.value:
        raise ValueError(f"Only value snaks are supported, got snaktype: {snak_json.get(JsonField.SNAKTYPE.value)}")

    datavalue = snak_json.get(JsonField.DATAVALUE.value, {})
    datatype = snak_json.get(JsonField.DATATYPE.value)
    value_type = datavalue.get(JsonField.VALUE.value, datatype)

    if value_type == "wikibase-entityid":
        return parse_entity_value(datavalue)
    elif datatype == Datatype.STRING:
        return parse_string_value(datavalue)
    elif value_type == "time":
        return parse_time_value(datavalue)
    elif value_type == "quantity":
        return parse_quantity_value(datavalue)
    elif value_type == "globecoordinate":
        return parse_globe_value(datavalue)
    elif value_type == "monolingualtext":
        return parse_monolingual_value(datavalue)
    elif datatype == Datatype.EXTERNAL_ID:
        return parse_external_id_value(datavalue)
    elif datatype == Datatype.COMMONS_MEDIA:
        return parse_commons_media_value(datavalue)
    elif datatype == Datatype.GEO_SHAPE:
        return parse_geo_shape_value(datavalue)
    elif datatype == Datatype.TABULAR_DATA:
        return parse_tabular_data_value(datavalue)
    elif datatype == Datatype.MUSICAL_NOTATION:
        return parse_musical_notation_value(datavalue)
    elif datatype == Datatype.URL:
        return parse_url_value(datavalue)
    elif datatype == Datatype.MATH:
        return parse_math_value(datavalue)
    elif datatype == Datatype.ENTITY_SCHEMA:
        return parse_entity_schema_value(datavalue)
    else:
        raise ValueError(f"Unsupported value type: {value_type}, datatype: {datatype}")
