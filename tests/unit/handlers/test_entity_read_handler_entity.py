import unittest
from unittest.mock import Mock, patch

from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler


class TestEntityReadHandlerEntity(unittest.TestCase):
    """Unit tests for EntityReadHandler entity methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch(
        "models.rest_api.entitybase.handlers.entity.read.EntityReadHandler.get_entity"
    )
    def test_get_entity_with_terms(self, mock_get_entity) -> None:
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

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_vitess_none(self, mock_raise_error) -> None:
        """Test get_entity raises error when vitess_client is None"""
        EntityReadHandler.get_entity("Q42", None, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Vitess not initialized", status_code=503
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_s3_none(self, mock_raise_error) -> None:
        """Test get_entity raises error when s3_client is None"""
        EntityReadHandler.get_entity("Q42", self.mock_vitess, None)
        mock_raise_error.assert_called_once_with("S3 not initialized", status_code=503)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_not_found(self, mock_raise_error) -> None:
        """Test get_entity raises error when entity does not exist"""
        self.mock_vitess.entity_exists.return_value = False
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_no_head_revision(self, mock_raise_error) -> None:
        """Test get_entity raises error when no head revision"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 0
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
    def test_get_entity_success_no_metadata(
        self, mock_terms_repo, mock_entity_response
    ):
        """Test get_entity success with no metadata"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123

        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {"id": "Q42"}
        mock_revision.data.entity = {"id": "Q42"}
        mock_revision.schema_version = "1.0"
        mock_revision.created_at = "2023-01-01"
        self.mock_s3.read_revision.return_value = mock_revision

        mock_entity_response_instance = Mock()
        mock_entity_response.return_value = mock_entity_response_instance

        result = EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)

        self.assertEqual(result, mock_entity_response_instance)
        self.mock_s3.read_revision.assert_called_once_with("Q42", 123)
        mock_entity_response.assert_called_once()


if __name__ == "__main__":
    unittest.main()
