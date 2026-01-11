"""JSON some value parser."""

from models.internal_representation.values import SomeValue


def parse_somevalue_value() -> SomeValue:
    """Parse some value from Wikidata JSON format."""
    return SomeValue()
