def wikibase_predicates(pid: str) -> dict[str, str]:
    return {
        "direct": f"wdt:{pid}",
        "statement": f"ps:{pid}",
        "statement_value": f"ps:{pid}",
        "qualifier": f"pq:{pid}",
        "reference": f"pr:{pid}",
        "statement_value_node": f"psv:{pid}",
    }
