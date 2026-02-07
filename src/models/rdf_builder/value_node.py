"""RDF value node writers."""

import hashlib
import logging
import re
from typing import Any

from models.rdf_builder.hashing.value_node_hasher import ValueNodeHasher

logger = logging.getLogger(__name__)


def format_scientific_notation(value: float) -> str:
    """Format value in scientific notation without leading zeros in exponent.

    Converts Python's 1.0E-05 format to Wikidata's 1.0E-5 format.

    Args:
        value: Numeric value to format

    Returns:
        String in scientific notation (e.g., "1.0E-5")
    """
    formatted = f"{value:.1E}"
    match = re.match(r"([+-]?[0-9.]+E)([+-])0([0-9]+)$", formatted)
    if match:
        mantissa = match.group(1)
        sign = match.group(2)
        exponent = match.group(3)
        return f"{mantissa}{sign}{exponent}"
    return formatted


def generate_value_node_uri(value: Any) -> str:
    """Generate wdv: URI for structured values using MD5 hash."""
    value_str = serialize_value(value)
    hash_val = hashlib.md5(value_str.encode("utf-8")).hexdigest()
    return hash_val


def serialize_value(value: Any) -> str:
    """Serialize value object to string for hashing.

    Uses MediaWiki-compatible format from ValueNodeHasher for structured values.
    """
    if hasattr(value, "kind"):
        kind = value.kind

        if kind == "time":
            parts = [
                f"t:{value.value}",
                str(value.precision),
                str(value.timezone),
                value.calendarmodel,
            ]
            return ":".join(parts)

        elif kind == "quantity":
            parts = [f"q:{value.value}:{value.unit}"]
            if value.upper_bound:
                parts.append(str(value.upper_bound))
            if value.lower_bound:
                parts.append(str(value.lower_bound))
            return ":".join(parts)

        elif kind == "globe":
            precision_formatted = format_scientific_notation(value.precision)
            return f"g:{value.latitude}:{value.longitude}:{precision_formatted}:{value.globe}"

    return str(value)
