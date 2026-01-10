from pydantic import Field

from models.rest_api.handlers.entity.enumeration import EnumerationHandler


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
