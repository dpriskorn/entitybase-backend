"""JSON property parser."""

from models.internal_representation.property_metadata import (
    PropertyMetadata,
    WikibaseDatatype,
)
from models.internal_representation.json_fields import JsonField


def parse_property(entity_json: dict) -> PropertyMetadata:
    """Parse property metadata from Wikidata JSON format."""
    return PropertyMetadata(
        property_id=entity_json[JsonField.ID.value],
        datatype=WikibaseDatatype(entity_json["datatype"]),
    )
