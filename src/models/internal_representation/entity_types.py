"""Enumeration of Wikibase entity types."""

from enum import Enum


class EntityType(str, Enum):
    """Type of entity.
    UNKNOWN is considered a bug"""
    ITEM = "item"
    PROPERTY = "property"
    LEXEME = "lexeme"
    UNKNOWN = "unknown"
    # ENTITY_SCHEMA = "entityschema"
