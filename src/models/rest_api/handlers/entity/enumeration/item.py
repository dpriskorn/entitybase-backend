from pydantic import Field

from models.rest_api.handlers.entity.enumeration import EnumerationHandler


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
