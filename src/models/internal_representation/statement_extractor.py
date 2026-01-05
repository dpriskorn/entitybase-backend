from collections import Counter

from models.internal_representation.entity import Entity


class StatementExtractor:
    @staticmethod
    def extract_properties(entity: Entity) -> list[str]:
        """Extract unique property IDs from entity statements

        Args:
            entity: Entity with statements

        Returns:
            Sorted list of unique property IDs (e.g., ["P31", "P569", "P19"])
        """
        properties = {stmt.property for stmt in entity.statements}
        return sorted(properties)

    @staticmethod
    def compute_property_counts(entity: Entity) -> dict[str, int]:
        """Count statements per property

        Args:
            entity: Entity with statements

        Returns:
            Dict mapping property ID -> statement count (e.g., {"P31": 2, "P569": 1})
        """
        counter = Counter(stmt.property for stmt in entity.statements)
        return dict(counter)
