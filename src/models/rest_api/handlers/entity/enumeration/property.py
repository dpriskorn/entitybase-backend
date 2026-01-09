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


class PropertyEnumerationHandler(EnumerationHandler):
    """Handles P ID enumeration for Wikibase properties."""

    min_id: int = Field(30000, description="Minimum value of the PID")

    @property
    def entity_type_prefix(self) -> str:
        return "P"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"P{self.min_id}"


class PropertyHandler(PropertyEnumerationHandler):
    """Handler for property ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"P{self.min_id}"
