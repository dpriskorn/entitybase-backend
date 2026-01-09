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


class EntitySchemaEnumerationHandler(EnumerationHandler):
    """Handles EID enumeration for Wikibase entity schemas."""

    min_id: int = Field(50000, description="Minimum value of the EID")

    @property
    def entity_type_prefix(self) -> str:
        return "E"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"E{self.min_id}"


class EntityschemaHandler(EntitySchemaEnumerationHandler):
    """Handler for entity schema ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"E{self.min_id}"
