"""Unit tests for statement service functions."""

import unittest
from unittest.mock import MagicMock, patch
from models.rest_api.v1.entitybase.services.statement_service import (
    deduplicate_references_in_statements,
)
from models.rest_api.v1.entitybase.response import StatementHashResult
from models.internal_representation.reference_hasher import ReferenceHasher


class TestStatementService(unittest.TestCase):
    """Unit tests for statement service functions."""

    def test_deduplicate_references_in_statements(self) -> None:
        """Test reference deduplication in statements."""
        # Mock S3 client
        mock_s3 = MagicMock()

        # Statement data with references
        statement_data = {
            "mainsnak": {"property": "P1"},
            "references": [
                {"hash": "oldhash1", "snaks": {"P1": []}},
                {"hash": "oldhash2", "snaks": {"P2": []}},
            ],
        }

        hash_result = StatementHashResult(
            statements=[123], full_statements=[statement_data]
        )

        # Mock hasher to return specific hashes
        with patch.object(ReferenceHasher, "compute_hash", side_effect=[456, 789]):
            result = deduplicate_references_in_statements(hash_result, mock_s3)

            self.assertTrue(result.success)
            # Check references replaced with hashes
            self.assertEqual(statement_data["references"], [456, 789])
            # Check S3 store calls
            self.assertEqual(mock_s3.store_reference.call_count, 2)
            mock_s3.store_reference.assert_any_call(
                456, {"hash": "oldhash1", "snaks": {"P1": []}}
            )
            mock_s3.store_reference.assert_any_call(
                789, {"hash": "oldhash2", "snaks": {"P2": []}}
            )


if __name__ == "__main__":
    unittest.main()
