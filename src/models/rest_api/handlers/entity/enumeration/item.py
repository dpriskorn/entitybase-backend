from .enumeration import ItemEnumerationHandler


class ItemHandler(ItemEnumerationHandler):
    """Handler for item ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"Q{self.min_id}"
