"""Extracts backlink information from Wikibase statements."""

from typing import Any


class StatementBacklinkExtractor:
    """Extracts backlink information from Wikibase statements."""

    @staticmethod
    def extract_backlink_data(statement: dict[str, Any]) -> list[tuple[str, str, str]]:
        """Extract backlink data from a statement JSON.

        Returns list of (referenced_entity_id, property_id, rank) tuples
        for all entity references in the statement.
        """
        rank = statement.get("rank", "normal")
        snaks = []

        # Add mainsnak
        if "mainsnak" in statement:
            snaks.append(statement["mainsnak"])

        # Add qualifiers
        qualifiers = statement.get("qualifiers", {})
        for qual_list in qualifiers.values():
            snaks.extend(qual_list)

        # Add references
        references = statement.get("references", [])
        for ref in references:
            ref_snaks = ref.get("snaks", {})
            for ref_list in ref_snaks.values():
                snaks.extend(ref_list)

        backlinks = []
        for snak in snaks:
            if snak.get("snaktype") == "value":
                datavalue = snak.get("datavalue")
                if datavalue and datavalue.get("type") == "wikibase-entityid":
                    value = datavalue.get("value", {})
                    entity_type = value.get("entity-type")
                    if entity_type in ("item", "property", "lexeme", "entity-schema"):
                        entity_id = value.get("id")
                        property_id = snak.get("property")
                        if entity_id and property_id:
                            backlinks.append((entity_id, property_id, rank))

        return backlinks
