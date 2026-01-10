from pydantic import Field

from models.rest_api.handlers.entity.enumeration import EnumerationHandler


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
