"""RDF ontology datatypes."""

import logging

from models.rest_api.utils import raise_validation_error
from models.rdf_builder.property_registry.models import (
    PropertyShape,
    PropertyPredicates,
)

logger = logging.getLogger(__name__)


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

    logger.debug("Creating PropertyPredicates from base")
    predicates = PropertyPredicates(**base)

    logger.debug(f"Checking datatype category for {datatype}")
    if datatype in {
        "wikibase-item",
        "wikibase-lexeme",
        "wikibase-form",
        "wikibase-sense",
        "wikibase-property",
        "commonsmedia",
        "string",
        "url",
        "math",
        "geo-shape",
        "monolingualtext",
        "tabular-data",
        "musical-notation",
        "entity-schema",
    }:
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=predicates,
            labels=labels or {},
            descriptions=descriptions or {},
        )

    if datatype == "external-id":
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(
                **base,
                value_node=f"psv:{pid}",
                qualifier_value=f"pqv:{pid}",
                reference_value=f"prv:{pid}",
                statement_normalized=f"psn:{pid}",
                qualifier_normalized=f"pqn:{pid}",
                reference_normalized=f"prn:{pid}",
                direct_normalized=f"wdtn:{pid}",
            ),
            labels=labels or {},
            descriptions=descriptions or {},
        )

    if datatype in {
        "time",
        "globe-coordinate",
    }:
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(
                **base,
                value_node=f"psv:{pid}",
                qualifier_value=f"pqv:{pid}",
                reference_value=f"prv:{pid}",
            ),
            labels=labels or {},
            descriptions=descriptions or {},
        )

    if datatype == "quantity":
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(
                **base,
                value_node=f"psv:{pid}",
                qualifier_value=f"pqv:{pid}",
                reference_value=f"prv:{pid}",
                statement_normalized=f"psn:{pid}",
                qualifier_normalized=f"pqn:{pid}",
                reference_normalized=f"prn:{pid}",
                direct_normalized=f"wdtn:{pid}",
            ),
            labels=labels or {},
            descriptions=descriptions or {},
        )

    raise_validation_error(f"Unsupported datatype: {datatype}")
