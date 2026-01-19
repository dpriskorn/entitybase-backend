"""RDF ontology Wikibase predicates."""

from models.rest_api.entitybase.v1.response import WikibasePredicatesResponse


def wikibase_predicates(pid: str) -> WikibasePredicatesResponse:
    """Create Wikibase predicates for a property ID."""
    return WikibasePredicatesResponse(
        direct=f"wdt:{pid}",
        statement=f"ps:{pid}",
        statement_value=f"ps:{pid}",
        qualifier=f"pq:{pid}",
        reference=f"pr:{pid}",
        statement_value_node=f"psv:{pid}",
    )
