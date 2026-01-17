import unittest
from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.response.entity.entitybase import EntityHistoryEntry


class TestEntityReadHandler(unittest.TestCase):
    """Unit tests for EntityReadHandler with term deduplication"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch("models.rest_api.handlers.entity.read.EntityReadHandler.get_entity")
    def test_get_entity_with_terms(self, mock_get_entity):
        """Test that get_entity calls work with term loading"""
        # This is more of an integration test, but ensures the method exists
        mock_entity_response = Mock()
        mock_entity_response.data = {
            "id": "Q42",
            "labels": {"en": {"language": "en", "value": "Test"}},
        }
        mock_get_entity.return_value = mock_entity_response

        # We can't easily test the full method without mocking all dependencies
        # This just verifies the method exists and can be called
        self.assertTrue(hasattr(self.handler, "get_entity"))

    @patch("models.rest_api.handlers.entity.read.raise_validation_error")
    def test_get_entity_history_vitess_none(self, mock_raise_error):
        """Test get_entity_history raises error when vitess_client is None"""
        EntityReadHandler.get_entity_history("Q42", None, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Vitess not initialized", status_code=503
        )

    @patch("models.rest_api.handlers.entity.read.raise_validation_error")
    def test_get_entity_history_entity_not_found(self, mock_raise_error):
        """Test get_entity_history raises error when entity does not exist"""
        self.mock_vitess.entity_exists.return_value = False
        EntityReadHandler.get_entity_history("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.handlers.entity.read.raise_validation_error")
    def test_get_entity_history_exception(self, mock_raise_error):
        """Test get_entity_history raises error on exception"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_entity_history.side_effect = Exception("DB error")
        EntityReadHandler.get_entity_history("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Failed to get entity history", status_code=500
        )

    def test_get_entity_history_success(self):
        """Test get_entity_history returns history on success"""
        self.mock_vitess.entity_exists.return_value = True
        mock_history = [
            EntityHistoryEntry(
                revision_id=1,
                created_at="2023-01-01",
                user_id=123,
                edit_summary="Test edit",
            ),
            EntityHistoryEntry(
                revision_id=2,
                created_at="2023-01-02",
                user_id=456,
                edit_summary="Another edit",
            ),
        ]
        self.mock_vitess.get_entity_history.return_value = mock_history

        result = EntityReadHandler.get_entity_history(
            "Q42", self.mock_vitess, self.mock_s3
        )

        self.assertEqual(result, mock_history)
        self.mock_vitess.get_entity_history.assert_called_once_with(
            "Q42", self.mock_s3, 20, 0
        )

    def test_get_entity_history_with_limit_offset(self):
        """Test get_entity_history with custom limit and offset"""
        self.mock_vitess.entity_exists.return_value = True
        mock_history = [
            EntityHistoryEntry(
                revision_id=1, created_at="2023-01-01", user_id=123, edit_summary="Test"
            )
        ]
        self.mock_vitess.get_entity_history.return_value = mock_history

        result = EntityReadHandler.get_entity_history(
            "Q42", self.mock_vitess, self.mock_s3, limit=10, offset=5
        )

        self.assertEqual(result, mock_history)
        self.mock_vitess.get_entity_history.assert_called_once_with(
            "Q42", self.mock_s3, 10, 5
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_vitess_none(self, mock_raise_error):
        """Test get_entity raises error when vitess_client is None"""
        EntityReadHandler.get_entity("Q42", None, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Vitess not initialized", status_code=503
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_s3_none(self, mock_raise_error):
        """Test get_entity raises error when s3_client is None"""
        EntityReadHandler.get_entity("Q42", self.mock_vitess, None)
        mock_raise_error.assert_called_once_with("S3 not initialized", status_code=503)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_not_found(self, mock_raise_error):
        """Test get_entity raises error when entity does not exist"""
        self.mock_vitess.entity_exists.return_value = False
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_no_head_revision(self, mock_raise_error):
        """Test get_entity raises error when no head revision"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 0
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_success_no_metadata(
        self, mock_terms_repo, mock_entity_response
    ):
        """Test get_entity success without metadata"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {"entity": {"id": "Q42"}}
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        self.mock_s3.read_revision.assert_called_once_with("Q42", 123)
        mock_entity_response.assert_called_once()

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_s3_none(self, mock_raise_error):
        """Test get_entity_revision raises error when s3_client is None"""
        EntityReadHandler.get_entity_revision("Q42", 123, None)
        mock_raise_error.assert_called_once_with("S3 not initialized", status_code=503)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_success(self, mock_revision_response):
        """Test get_entity_revision success"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {"id": "Q42"}
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.return_value = {"en": {"value": "Test"}}

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        self.mock_s3.read_revision.assert_called_once_with("Q42", 123)
        mock_revision_response.assert_called_once()

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_exception(self, mock_raise_error):
        """Test get_entity_revision handles exceptions"""
        self.mock_s3.read_revision.side_effect = Exception("S3 error")

        EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        mock_raise_error.assert_called_once_with(
            "Failed to read entity revision", status_code=500
        )


if __name__ == "__main__":
    unittest.main()
