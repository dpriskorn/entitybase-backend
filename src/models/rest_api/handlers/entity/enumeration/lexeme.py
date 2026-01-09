from .enumeration import LexemeEnumerationHandler


class LexemeHandler(LexemeEnumerationHandler):
    """Handler for lexeme ID enumeration."""

    @property
    def next_entity_id(self) -> str:
        # TODO: Implement database-backed ID generation
        return f"L{self.min_id}"
