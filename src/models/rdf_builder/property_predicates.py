# src/models/rdf_builder/property_predicates.py

from dataclasses import dataclass


@dataclass(frozen=True)
class PredicateSet:
    claim: str
    statement: str
    qualifier: str
    direct: str
    reference: str


DATATYPE_PREDICATES = {
    "wikibase-item": PredicateSet(
        claim="p",
        statement="ps",
        qualifier="pq",
        direct="wdt",
        reference="pr",
    ),
    "string": PredicateSet(
        claim="p",
        statement="ps",
        qualifier="pq",
        direct="wdt",
        reference="pr",
    ),
    # all datatypes map identically at predicate level
}
