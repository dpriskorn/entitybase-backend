from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from models.rest_api.handlers.entity.enumeration import EnumerationHandler


class LexemeEnumerationHandler(EnumerationHandler):
    """Handles L ID enumeration for Wikibase lexemes."""

    min_id: int = Field(5000000, description="Minimum value of the LID")

    @property
    def entity_type_prefix(self) -> str:
        return "L"

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"L{self.min_id}"
