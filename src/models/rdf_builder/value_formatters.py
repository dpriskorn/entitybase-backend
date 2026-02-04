"""RDF value formatters."""

import logging
from collections.abc import Callable
from typing import Any
from models.internal_representation.value_kinds import ValueKind

logger = logging.getLogger(__name__)


class ValueFormatter:
    """Format internal Value objects as RDF literals/URIs."""

    @staticmethod
    def _format_entity(value: Any) -> str:
        return f"wd:{value.value}"

    @staticmethod
    def _format_string(value: Any) -> str:
        escaped = ValueFormatter.escape_turtle(value.value)
        return f'"{escaped}"'

    @staticmethod
    def _format_time(value: Any) -> str:
        return f'"{value.value}"^^xsd:dateTime'

    @staticmethod
    def _format_quantity(value: Any) -> str:
        return f"{value.value}^^xsd:decimal"

    @staticmethod
    def _format_globe(value: Any) -> str:
        coord = f"Point({value.longitude} {value.latitude})"
        formatted = f'"{coord}"^^geo:wktLiteral'
        logger.debug(
            f"GLOBE value formatting: lat={value.latitude}, lon={value.longitude} -> {formatted}"
        )
        return formatted

    @staticmethod
    def _format_monolingual(value: Any) -> str:
        escaped = ValueFormatter.escape_turtle(value.text)
        return f'"{escaped}"@{value.language}'

    @staticmethod
    def _format_external_id(value: Any) -> str:
        escaped = ValueFormatter.escape_turtle(value.value)
        return f'"{escaped}"'

    @staticmethod
    def _format_commons_media(value: Any) -> str:
        file = ValueFormatter.escape_turtle(value.value)
        return f'"{file}"'

    @staticmethod
    def _format_geo_shape(value: Any) -> str:
        shape = ValueFormatter.escape_turtle(value.value)
        return f'"{shape}"'

    @staticmethod
    def _format_url(value: Any) -> str:
        url = ValueFormatter.escape_turtle(value.value)
        return f'"{url}"'

    @staticmethod
    def _format_novalue(value: Any) -> str:
        return "wikibase:noValue"

    @staticmethod
    def _format_somevalue(value: Any) -> str:
        return "wikibase:someValue"

    _FORMATTERS: dict[ValueKind, Callable[[Any], str]] = {
        ValueKind.ENTITY: _format_entity,
        ValueKind.STRING: _format_string,
        ValueKind.TIME: _format_time,
        ValueKind.QUANTITY: _format_quantity,
        ValueKind.GLOBE: _format_globe,
        ValueKind.MONOLINGUAL: _format_monolingual,
        ValueKind.EXTERNAL_ID: _format_external_id,
        ValueKind.COMMONS_MEDIA: _format_commons_media,
        ValueKind.GEO_SHAPE: _format_geo_shape,
        ValueKind.URL: _format_url,
        ValueKind.NOVALUE: _format_novalue,
        ValueKind.SOMEVALUE: _format_somevalue,
    }

    @staticmethod
    def format_value(value: Any) -> str:
        formatter = ValueFormatter._FORMATTERS.get(value.kind)
        if formatter:
            return formatter(value)
        return ""

    @staticmethod
    def escape_turtle(value: str) -> str:
        """Escape special characters for Turtle format."""
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        value = value.replace("\r", "\\r")
        value = value.replace("\t", "\\t")
        return value
