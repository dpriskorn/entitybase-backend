"""Unit tests for patch_statement endpoint."""

import unittest
from unittest.mock import MagicMock, patch
from models.rest_api.entitybase.handlers.entity.handler import EntityHandler
from models.rest_api.entitybase.request.entity.patch_statement import (
    PatchStatementRequest,
)
from models.common import OperationResult
from models.rest_api.entitybase.response import EntityResponse, EntityState


class TestPatchStatement(unittest.TestCase):
    """Unit tests for patch_statement functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = EntityHandler()
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_validator = MagicMock()

    def test_statement_hash_not_found(self):
        """Test statement hash not found."""
        request = PatchStatementRequest(
            claim={"mainsnak": {"property": "P1"}}, edit_summary="Patch"
        )

        with patch(
            "models.rest_api.entitybase.handlers.entity.handler.EntityReadHandler"
        ) as mock_read_handler_class:
            mock_read_handler = MagicMock()
            mock_read_handler_class.return_value = mock_read_handler
            mock_entity_response = MagicMock()
            mock_entity_response.entity_data = {
                "claims": {"P1": [{"mainsnak": {"property": "P1"}}]}
            }
            mock_read_handler.get_entity.return_value = mock_entity_response

            result = self.handler.patch_statement(
                "Q1", "999", request, self.mock_vitess, self.mock_s3
            )
            self.assertFalse(result.success)
            self.assertIn("Statement not found", result.error)

    @patch("models.rest_api.entitybase.handlers.entity.handler.EntityReadHandler")
    @patch.object(EntityHandler, "_create_and_store_revision")
    @patch.object(EntityHandler, "process_statements")
    @patch(
        "models.internal_representation.statement_hasher.StatementHasher.compute_hash"
    )
    def test_successful_patch_statement(
        self, mock_hash, mock_process, mock_create, mock_read_handler_class
    ):
        """Test successful statement patching."""
        mock_read_handler = MagicMock()
        mock_read_handler_class.return_value = mock_read_handler

        mock_entity_response = MagicMock()
        mock_entity_response.revision_id = 100
        mock_entity_response.entity_data = {
            "claims": {"P1": [{"mainsnak": {"property": "P1"}}]},
            "type": "item",
        }
        mock_entity_response.state = EntityState()
        mock_read_handler.get_entity.return_value = mock_entity_response

        mock_hash.return_value = 123  # Matches the hash parameter

        mock_process.return_value = MagicMock()

        mock_revision_result = MagicMock()
        mock_revision_result.success = True
        mock_revision_result.data.rev_id = 101
        mock_create.return_value = mock_revision_result

        request = PatchStatementRequest(
            claim={"mainsnak": {"property": "P1", "value": "new value"}},
            edit_summary="Patched statement",
        )

        result = self.handler.patch_statement(
            "Q1", "123", request, self.mock_vitess, self.mock_s3
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data, {"revision_id": 101})
        mock_create.assert_called_once()
        # Verify claim was replaced
        self.assertEqual(
            mock_entity_response.entity_data["claims"]["P1"][0], request.claim
        )


if __name__ == "__main__":
    unittest.main()
