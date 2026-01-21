"""Vitess terms repository for managing deduplicated terms."""

from typing import List

from models.common import OperationResult
from models.infrastructure.vitess.repository import Repository
from models.rest_api.entitybase.v1.response.misc import TermsResponse


class TermsRepository(Repository):
    """Repository for managing deduplicated terms (labels and aliases) in Vitess."""

    def insert_term(
        self, hash_value: int, term: str, term_type: str
    ) -> OperationResult:
        """Insert a term if it doesn't already exist."""
        try:
            cursor = self.vitess_client.cursor
            cursor.execute(
                """
                INSERT INTO entity_terms (hash, term, term_type)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE hash = hash
                """,
                (hash_value, term, term_type),
            )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_term(self, hash_value: int) -> tuple[str, str] | None:
        """Retrieve a term and its type by hash."""
        cursor = self.vitess_client.cursor
        cursor.execute(
            "SELECT term, term_type FROM entity_terms WHERE hash = %s",
            (hash_value,),
        )
        result = cursor.fetchone()
        return (result[0], result[1]) if result else None

    def batch_get_terms(self, hashes: List[int]) -> TermsResponse:
        """Retrieve multiple terms by their hashes."""
        if not hashes:
            return TermsResponse(terms={})
        cursor = self.vitess_client.cursor
        # Create placeholders for the IN clause
        placeholders = ",".join(["%s"] * len(hashes))
        cursor.execute(
            f"SELECT hash, term, term_type FROM entity_terms WHERE hash IN ({placeholders})",
            hashes,
        )
        results = cursor.fetchall()
        return TermsResponse(terms={row[0]: (row[1], row[2]) for row in results})

    def hash_exists(self, hash_value: int) -> bool:
        """Check if a hash exists in the terms table."""
        cursor = self.vitess_client.cursor
        cursor.execute(
            "SELECT 1 FROM entity_terms WHERE hash = %s LIMIT 1",
            (hash_value,),
        )
        return cursor.fetchone() is not None
