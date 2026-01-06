from typing import Any

from models.json_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.registry import PropertyRegistry


def serialize_entity_to_turtle(
    entity_data: dict[str, Any],
    entity_id: str,
    property_registry: PropertyRegistry | None = None,
) -> str:
    """Convert entity data dict to Turtle format string."""
    entity = parse_entity(entity_data)
    converter = EntityConverter(
        property_registry=property_registry or PropertyRegistry(properties={}),
        enable_deduplication=True,
    )
    return str(converter.convert_to_string(entity))
