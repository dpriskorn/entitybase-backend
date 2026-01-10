"""Enumeration of Wikibase entity types."""

from enum import Enum


class EntityKind(str, Enum):
    ITEM = "item"
    PROPERTY = "property"
    LEXEME = "lexeme"
    ENTITY_SCHEMA = "entityschema"
