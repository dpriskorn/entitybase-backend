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

    min_id: int = Field(300000000, description="Minimum value of the QID")

    @property
    def entity_type_prefix(self) -> str:
        return "Q"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        # For now, return a placeholder
        return f"Q{self.min_id}"


class ItemHandler(ItemEnumerationHandler):
    """Handler for item ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"Q{self.min_id}"
