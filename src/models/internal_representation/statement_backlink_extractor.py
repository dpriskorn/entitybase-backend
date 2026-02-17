"""Extracts backlink information from Wikibase statements."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class StatementBacklinkExtractor:
    """Extracts backlink information from Wikibase statements."""

    @staticmethod
    def _collect_all_snaks(statement: dict[str, Any]) -> list[dict[str, Any]]:
        """Collect all snaks from a statement (mainsnak, qualifiers, references).

        Args:
            statement: Statement dictionary

        Returns:
            List of all snak dictionaries
        """
        snaks = []

        if "mainsnak" in statement:
            snaks.append(statement["mainsnak"])

        qualifiers = statement.get("qualifiers", {})
        for qual_list in qualifiers.values():
            snaks.extend(qual_list)

        references = statement.get("references", [])
        for ref in references:
            ref_snaks = ref.get("snaks", {})
            for ref_list in ref_snaks.values():
                snaks.extend(ref_list)

        return snaks

    @staticmethod
    def _extract_backlinks_from_snaks(
        snaks: list[dict[str, Any]], rank: str
    ) -> list[tuple[str, str, str]]:
        """Extract entity backlinks from list of snaks.

        Args:
            snaks: List of snak dictionaries
            rank: Statement rank

        Returns:
            List of (entity_id, property_id, rank) tuples
        """
        backlinks = []
        valid_entity_types = ("item", "property", "lexeme", "entity-schema")

        for snak in snaks:
            if snak.get("snaktype") != "value":
                continue

            datavalue = snak.get("datavalue")
            if not datavalue or datavalue.get("type") != "wikibase-entityid":
                continue

            value = datavalue.get("value", {})
            entity_type = value.get("entity-type")

            if entity_type not in valid_entity_types:
                continue

            entity_id = value.get("id")
            property_id = snak.get("property")

            if entity_id and property_id:
                backlinks.append((entity_id, property_id, rank))

        return backlinks

    @staticmethod
    def extract_backlink_data(statement: dict[str, Any]) -> list[tuple[str, str, str]]:
        """Extract backlink data from a statement JSON.

        Returns list of (referenced_entity_id, property_id, rank) tuples
        for all entity references in the statement.
        """
        logger.debug("Extracting backlink data from statement")
        rank = statement.get("rank", "normal")

        snaks = StatementBacklinkExtractor._collect_all_snaks(statement)
        backlinks = StatementBacklinkExtractor._extract_backlinks_from_snaks(
            snaks, rank
        )

        return backlinks
