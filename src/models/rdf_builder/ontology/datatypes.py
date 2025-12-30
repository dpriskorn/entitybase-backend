from models.rdf_builder.property_registry.models import (
    PropertyShape,
    PropertyPredicates,
)


def property_shape(pid: str, datatype: str) -> PropertyShape:
    base = {
        "direct": f"wdt:{pid}",
        "statement": f"ps:{pid}",
        "qualifier": f"pq:{pid}",
        "reference": f"pr:{pid}",
    }

    if datatype in {
        "wikibase-item",
        "string",
        "external-id",
        "monolingualtext",
    }:
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(**base),
        )

    if datatype in {"time", "globe-coordinate"}:
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(
                **base,
                value_node=f"psv:{pid}",
            ),
        )

    raise ValueError(f"Unsupported datatype: {datatype}")
