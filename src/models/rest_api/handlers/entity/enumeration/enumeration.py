from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class EnumerationHandler(ABC, BaseModel):
    """Abstract base class for entity ID enumeration handlers."""

    min_id: int = Field(..., description="Minimum ID value (inclusive)")

    @property
    @abstractmethod
    def next_entity_id(self) -> str:
        """Generate and return the next available entity ID."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def entity_type_prefix(self) -> str:
        """Return the single-character prefix for this entity type."""
        raise NotImplementedError()


class ItemEnumerationHandler(EnumerationHandler):
    """Handles Q ID enumeration for Wikibase items."""

    min_id: int = 1

    @property
    def entity_type_prefix(self) -> str:
        return "Q"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        # For now, return a placeholder
        return f"Q{self.min_id}"


class PropertyEnumerationHandler(EnumerationHandler):
    """Handles P ID enumeration for Wikibase properties."""

    min_id: int = 1

    @property
    def entity_type_prefix(self) -> str:
        return "P"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"P{self.min_id}"


class LexemeEnumerationHandler(EnumerationHandler):
    """Handles L ID enumeration for Wikibase lexemes."""

    min_id: int = 1

    @property
    def entity_type_prefix(self) -> str:
        return "L"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"L{self.min_id}"


class EntitySchemaEnumerationHandler(EnumerationHandler):
    """Handles E ID enumeration for Wikibase entity schemas."""

    min_id: int = 1

    @property
    def entity_type_prefix(self) -> str:
        return "E"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"E{self.min_id}"
