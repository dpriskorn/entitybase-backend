from .enumeration import EntitySchemaEnumerationHandler


class EntityschemaHandler(EntitySchemaEnumerationHandler):
    """Handler for entity schema ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"E{self.min_id}"
