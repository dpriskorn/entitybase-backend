"""JSON no value parser."""

from models.internal_representation.values import NoValue


def parse_novalue_value() -> NoValue:
    """Parse no value from Wikidata JSON format."""
    return NoValue()
