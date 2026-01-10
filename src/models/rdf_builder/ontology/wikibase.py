from models.api_models import WikibasePredicates


def wikibase_predicates(pid: str) -> WikibasePredicates:
    return WikibasePredicates(
        direct=f"wdt:{pid}",
        statement=f"ps:{pid}",
        statement_value=f"ps:{pid}",
        qualifier=f"pq:{pid}",
        reference=f"pr:{pid}",
        statement_value_node=f"psv:{pid}",
    )
