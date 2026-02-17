"""RDF ontology datatypes."""

import logging

from models.rest_api.utils import raise_validation_error
from models.rdf_builder.property_registry.models import (
    PropertyShape,
    PropertyPredicates,
)

logger = logging.getLogger(__name__)

ITEM_DATATYPES = frozenset(
    {
        "wikibase-item",
        "wikibase-lexeme",
        "wikibase-form",
        "wikibase-sense",
        "wikibase-property",
        "commonsmedia",
        "commonsMedia",
        "string",
        "url",
        "math",
        "geo-shape",
        "monolingualtext",
        "external-id",
        "tabular-data",
        "musical-notation",
        "entity-schema",
    }
)

EXTERNAL_ID_DATATYPES = frozenset({"external-id"})


def _build_item_predicates(base: dict[str, str]) -> PropertyPredicates:
    """Build predicates for item-type datatypes.

    Args:
        base: Base predicate dictionary

    Returns:
        PropertyPredicates with base predicates only
    """
    return PropertyPredicates(**base)


def _build_external_id_predicates(base: dict[str, str], pid: str) -> PropertyPredicates:
    """Build predicates for external-id datatype.

    Args:
        base: Base predicate dictionary
        pid: Property ID

    Returns:
        PropertyPredicates with all extra predicates
    """
    return PropertyPredicates(
        **base,
        value_node=f"psv:{pid}",
        qualifier_value=f"pqv:{pid}",
        reference_value=f"prv:{pid}",
        statement_normalized=f"psn:{pid}",
        qualifier_normalized=f"pqn:{pid}",
        reference_normalized=f"prn:{pid}",
        direct_normalized=f"wdtn:{pid}",
    )


def _build_time_predicates(base: dict[str, str], pid: str) -> PropertyPredicates:
    """Build predicates for time datatype.

    Args:
        base: Base predicate dictionary
        pid: Property ID

    Returns:
        PropertyPredicates with value node predicates
    """
    return PropertyPredicates(
        **base,
        value_node=f"psv:{pid}",
        qualifier_value=f"pqv:{pid}",
        reference_value=f"prv:{pid}",
    )


def _build_quantity_predicates(base: dict[str, str], pid: str) -> PropertyPredicates:
    """Build predicates for quantity datatype.

    Args:
        base: Base predicate dictionary
        pid: Property ID

    Returns:
        PropertyPredicates with all quantity-specific predicates
    """
    return PropertyPredicates(
        **base,
        value_node=f"psv:{pid}",
        qualifier_value=f"pqv:{pid}",
        reference_value=f"prv:{pid}",
        statement_normalized=f"psn:{pid}",
        qualifier_normalized=f"pqn:{pid}",
        reference_normalized=f"prn:{pid}",
        direct_normalized=f"wdtn:{pid}",
    )


def property_shape(
    pid: str,
    datatype: str,
    labels: dict[str, dict] | None = None,
    descriptions: dict[str, dict] | None = None,
) -> PropertyShape:
    """Create a PropertyShape with appropriate predicates for datatype.

    Args:
        pid: Property ID (e.g., P31)
        datatype: Datatype name (e.g., wikibase-item)
        labels: Labels by language
        descriptions: Descriptions by language

    Returns:
        PropertyShape with predicates configured for datatype
    """
    logger.debug(f"Creating property shape for {pid} with datatype {datatype}")
    logger.debug("Building base predicates")
    base = {
        "direct": f"wdt:{pid}",
        "statement": f"ps:{pid}",
        "qualifier": f"pq:{pid}",
        "reference": f"pr:{pid}",
    }

    logger.debug(f"Checking datatype category for {datatype}")
    if datatype in ITEM_DATATYPES:
        predicates = _build_item_predicates(base)
    elif datatype in EXTERNAL_ID_DATATYPES:
        predicates = _build_external_id_predicates(base, pid)
    elif datatype in {"time", "globe-coordinate"}:
        predicates = _build_time_predicates(base, pid)
    elif datatype == "quantity":
        predicates = _build_quantity_predicates(base, pid)
    else:
        raise_validation_error(f"Unsupported datatype: {datatype}")

    return PropertyShape(
        pid=pid,
        datatype=datatype,
        predicates=predicates,
        labels=labels or {},
        descriptions=descriptions or {},
    )
