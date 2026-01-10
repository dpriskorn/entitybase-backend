from models.api_models import PropertyCounts


class StatementExtractor:
    @staticmethod
    def extract_properties_from_claims(claims: dict[str, list]) -> list[str]:
        """Extract unique property IDs from raw claims dict

        Args:
            claims: Dict mapping property ID to list of statements

        Returns:
            Sorted list of unique property IDs with non-empty claim lists
        """
        return sorted(
            [property_id for property_id, claim_list in claims.items() if claim_list]
        )

    @staticmethod
    def compute_property_counts_from_claims(claims: dict[str, list]) -> PropertyCounts:
        """Count statements per property from raw claims dict

        Args:
            claims: Dict mapping property ID to list of statements

        Returns:
            PropertyCounts with counts mapping property ID -> statement count for non-empty claim lists
        """
        counts = {
            property_id: len(claim_list)
            for property_id, claim_list in claims.items()
            if claim_list
        }
        return PropertyCounts(counts=counts)
