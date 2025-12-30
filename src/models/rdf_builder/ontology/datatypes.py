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
        "wikibase-string",
        "string",
        "external-id",
        "wikibase-monolingualtext",
        "monolingualtext",
        "commonsmedia",
        "globecoordinate",
        "quantity",
        "url",
        "math",
        "musical-notation",
        "geo-shape",
        "geoshape",
        "tabular-data",
        "tabulardata",
        "wikibase-lexeme",
        "wikibaselexeme",
        "wikibase-form",
        "wikibaseform",
        "wikibase-sense",
        "wikibasesense",
        "wikibase-property",
        "entity-schema",
    }:
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(**base),
        )

    if datatype in {
        "time",
        "globe-coordinate",
        "wikibase-globe-coordinate",
    }:
        return PropertyShape(
            pid=pid,
            datatype=datatype,
            predicates=PropertyPredicates(
                **base,
                value_node=f"psv:{pid}",
            ),
        )

    raise ValueError(f"Unsupported datatype: {datatype}")
