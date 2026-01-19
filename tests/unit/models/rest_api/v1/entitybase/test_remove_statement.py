"""Unit tests for remove_statement endpoint."""

import unittest
from unittest.mock import MagicMock, patch
from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler
from models.rest_api.entitybase.v1.request.entity.remove_statement import (
    RemoveStatementRequest,
)


class TestRemoveStatement(unittest.TestCase):
    """Unit tests for remove_statement functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = EntityHandler()
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_validator = MagicMock()

    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.read_revision"
    )
    def test_statement_not_found(self, mock_read_revision) -> None:
        """Test statement not found in revision."""
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes

        mock_revision = RevisionData(
            revision_id=100,
            entity_type="item",
            properties=["P1"],
            property_counts={"P1": 1},
            hashes=HashMaps(statements=StatementsHashes(root=[123])),
            edit=MagicMock(),
            state=MagicMock(),
        )
        mock_read_revision.return_value = mock_revision
        self.mock_vitess.get_head.return_value = 100

        request = RemoveStatementRequest(edit_summary="Remove statement")
        result = self.handler.remove_statement(
            "Q1", "999", request.edit_summary, self.mock_vitess, self.mock_s3
        )
        self.assertFalse(result.success)
        self.assertIn("Statement hash not found", result.error)

    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.read_revision"
    )
    @patch("models.rest_api.entitybase.v1.handlers.entity.handler.StatementRepository")
    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.store_revision"
    )
    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.VitessClient.update_head_revision"
    )
    def test_successful_remove_statement(
        self,
        mock_update_head,
        mock_store_revision,
        mock_stmt_repo_class,
        mock_read_revision,
    ):
        """Test successful statement removal."""
        # Mock revision data
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes

        mock_revision = RevisionData(
            revision_id=100,
            entity_type="item",
            properties=["P1", "P2"],
            property_counts={"P1": 1, "P2": 1},
            hashes=HashMaps(statements=StatementsHashes(root=[123, 456])),
            edit=MagicMock(),
            state=MagicMock(),
        )
        mock_read_revision.return_value = mock_revision
        self.mock_vitess.get_head.return_value = 100

        # Mock statement repository
        mock_stmt_repo = MagicMock()
        mock_stmt_repo_class.return_value = mock_stmt_repo
        mock_stmt_repo.decrement_ref_count.return_value = MagicMock(success=True)

        request = RemoveStatementRequest(edit_summary="Remove statement")
        result = self.handler.remove_statement(
            "Q1", "123", request.edit_summary, self.mock_vitess, self.mock_s3
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data, {"revision_id": 101})
        # Check statements updated
        self.assertEqual(mock_revision.hashes.statements.root, [456])
        # Check property counts updated: P1 removed since count became 0
        self.assertEqual(mock_revision.properties, ["P2"])
        self.assertEqual(mock_revision.property_counts, {"P2": 1})
        mock_stmt_repo.decrement_ref_count.assert_called_once_with(123)
        mock_store_revision.assert_called_once()
        mock_update_head.assert_called_once_with("Q1", 101)

    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.read_revision"
    )
    def test_statement_hash_not_found(self, mock_read_revision) -> None:
        """Test statement hash not found in revision."""
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes

        mock_revision = RevisionData(
            revision_id=100,
            entity_type="item",
            properties=["P1"],
            property_counts={"P1": 1},
            hashes=HashMaps(statements=StatementsHashes(root=[123])),
            edit=MagicMock(),
            state=MagicMock(),
        )
        mock_read_revision.return_value = mock_revision
        self.mock_vitess.get_head.return_value = 100

        request = RemoveStatementRequest(edit_summary="Remove statement")
        result = self.handler.remove_statement(
            "Q1", "999", request.edit_summary, self.mock_vitess, self.mock_s3
        )

        self.assertFalse(result.success)
        self.assertIn("Statement hash not found", result.error)

    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.read_revision"
    )
    @patch("models.rest_api.entitybase.v1.handlers.entity.handler.StatementRepository")
    def test_decrement_ref_count_failure(
        self, mock_stmt_repo_class, mock_read_revision
    ):
        """Test failure when decrementing ref_count."""
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes

        mock_revision = RevisionData(
            revision_id=100,
            entity_type="item",
            properties=["P1"],
            property_counts={"P1": 1},
            hashes=HashMaps(statements=StatementsHashes(root=[123])),
            edit=MagicMock(),
            state=MagicMock(),
        )
        mock_read_revision.return_value = mock_revision
        self.mock_vitess.get_head.return_value = 100

        mock_stmt_repo = MagicMock()
        mock_stmt_repo_class.return_value = mock_stmt_repo
        mock_stmt_repo.decrement_ref_count.return_value = MagicMock(
            success=False, error="DB error"
        )

        request = RemoveStatementRequest(edit_summary="Remove statement")
        with self.assertRaises(
            Exception
        ):  # raise_validation_error raises HTTPException
            self.handler.remove_statement(
                "Q1", "123", request.edit_summary, self.mock_vitess, self.mock_s3
            )

    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.read_revision"
    )
    def test_invalid_statement_hash_format(self, mock_read_revision) -> None:
        """Test invalid statement hash format."""
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes

        mock_revision = RevisionData(
            revision_id=100,
            entity_type="item",
            properties=["P1"],
            property_counts={"P1": 1},
            hashes=HashMaps(statements=StatementsHashes(root=[123])),
            edit=MagicMock(),
            state=MagicMock(),
        )
        mock_read_revision.return_value = mock_revision

        request = RemoveStatementRequest(edit_summary="Remove statement")
        result = self.handler.remove_statement(
            "Q1", "invalid", request.edit_summary, self.mock_vitess, self.mock_s3
        )

        self.assertFalse(result.success)
        self.assertIn("Invalid statement hash format", result.error)

    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.handler.MyS3Client.read_revision"
    )
    def test_no_statements_in_revision(self, mock_read_revision) -> None:
        """Test revision with no statements."""
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.infrastructure.s3.hashes.hash_maps import HashMaps

        mock_revision = RevisionData(
            revision_id=100,
            entity_type="item",
            properties=[],
            property_counts={},
            hashes=HashMaps(statements=None),
            edit=MagicMock(),
            state=MagicMock(),
        )
        mock_read_revision.return_value = mock_revision
        self.mock_vitess.get_head.return_value = 100

        request = RemoveStatementRequest(edit_summary="Remove statement")
        result = self.handler.remove_statement(
            "Q1", "123", request.edit_summary, self.mock_vitess, self.mock_s3
        )

        self.assertFalse(result.success)
        self.assertIn("No statements found in revision", result.error)


if __name__ == "__main__":
    unittest.main()
