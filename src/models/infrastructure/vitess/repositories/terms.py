"""Vitess terms repository for managing deduplicated terms."""

import logging
from typing import List

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository
from models.data.rest_api.v1.entitybase.response import TermsResponse

logger = logging.getLogger(__name__)


class TermsRepository(Repository):
    """Repository for managing deduplicated terms (labels and aliases) in Vitess."""

    def insert_term(
        self, hash_value: int, term: str, term_type: str
    ) -> OperationResult:
        """Insert a term if it doesn't already exist, or increment ref_count."""
        if hash_value <= 0:
            return OperationResult(success=False, error="Invalid hash value")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    """
                    INSERT INTO entity_terms (hash, term, term_type, ref_count)
                    VALUES (%s, %s, %s, 1)
                    ON DUPLICATE KEY UPDATE ref_count = ref_count + 1
                    """,
                    (hash_value, term, term_type),
                )
                return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def increment_ref_count(self, hash_value: int) -> OperationResult:
        """Increment reference count for a term."""
        if hash_value <= 0:
            return OperationResult(success=False, error="Invalid hash value")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "UPDATE entity_terms SET ref_count = ref_count + 1 WHERE hash = %s",
                    (hash_value,),
                )
                cursor.execute(
                    "SELECT ref_count FROM entity_terms WHERE hash = %s",
                    (hash_value,),
                )
                result = cursor.fetchone()
                new_count = result[0] if result else 0
                return OperationResult(success=True, data=new_count)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def decrement_ref_count(self, hash_value: int) -> OperationResult:
        """Decrement reference count for a term."""
        if hash_value <= 0:
            return OperationResult(success=False, error="Invalid hash value")

        logger.debug(f"Decrementing ref count for term hash {hash_value}")
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "UPDATE entity_terms SET ref_count = ref_count - 1 WHERE hash = %s",
                    (hash_value,),
                )
                cursor.execute(
                    "SELECT ref_count FROM entity_terms WHERE hash = %s",
                    (hash_value,),
                )
                result = cursor.fetchone()
                new_count = result[0] if result else 0
                return OperationResult(success=True, data=new_count)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_ref_count(self, hash_value: int) -> int:
        """Get the reference count for a term."""
        if hash_value <= 0:
            return 0

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "SELECT ref_count FROM entity_terms WHERE hash = %s",
                (hash_value,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_orphaned(self, older_than_days: int, limit: int) -> OperationResult:
        """Get orphaned term hashes where ref_count is 0."""
        if older_than_days <= 0 or limit <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    """SELECT hash, term_type
                            FROM entity_terms
                            WHERE ref_count = 0
                            AND created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                            LIMIT %s""",
                    (older_than_days, limit),
                )
                result = [(row[0], row[1]) for row in cursor.fetchall()]
                return OperationResult(success=True, data=result)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def delete_term(self, hash_value: int) -> None:
        """Delete a term when ref_count reaches 0."""
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "DELETE FROM entity_terms WHERE hash = %s AND ref_count <= 0",
                (hash_value,),
            )
