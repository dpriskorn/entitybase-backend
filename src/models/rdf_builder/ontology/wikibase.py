"""RDF ontology Wikibase predicates."""

from models.rest_api.response import WikibasePredicates


def wikibase_predicates(pid: str) -> WikibasePredicates:
    """Create Wikibase predicates for a property ID."""
    return WikibasePredicates(
        direct=f"wdt:{pid}",
        statement=f"ps:{pid}",
        statement_value=f"ps:{pid}",
        qualifier=f"pq:{pid}",
        reference=f"pr:{pid}",
        statement_value_node=f"psv:{pid}",
    )
