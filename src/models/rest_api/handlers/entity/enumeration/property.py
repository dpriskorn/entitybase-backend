from .enumeration import PropertyEnumerationHandler


class PropertyHandler(PropertyEnumerationHandler):
    """Handler for property ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"P{self.min_id}"
