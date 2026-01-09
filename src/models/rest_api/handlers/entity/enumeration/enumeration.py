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
