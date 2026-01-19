import unittest
from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler


class TestEntityReadHandlerRevision(unittest.TestCase):
    """Unit tests for EntityReadHandler revision methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_s3_none(self, mock_raise_error) -> None:
        """Test get_entity_revision raises error when s3_client is None"""
        EntityReadHandler.get_entity_revision("Q42", 123, None)
        mock_raise_error.assert_called_once_with("S3 not initialized", status_code=503)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_success(self, mock_revision_response) -> None:
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
    def test_get_entity_revision_exception(self, mock_raise_error) -> None:
        """Test get_entity_revision handles exceptions"""
        self.mock_s3.read_revision.side_effect = Exception("S3 error")

        EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        mock_raise_error.assert_called_once_with("Revision not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_invalid_revision_id_zero(self, mock_raise_error) -> None:
        """Test get_entity_revision with invalid revision_id 0"""
        EntityReadHandler.get_entity_revision("Q42", 0, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Invalid revision ID: 0", status_code=400
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_invalid_revision_id_negative(self, mock_raise_error) -> None:
        """Test get_entity_revision with negative revision_id"""
        EntityReadHandler.get_entity_revision("Q42", -1, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Invalid revision ID: -1", status_code=400
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_revision_too_high(self, mock_raise_error) -> None:
        """Test get_entity_revision when revision > current head"""
        self.mock_s3.read_revision.side_effect = Exception("Revision not found")

        EntityReadHandler.get_entity_revision("Q42", 11, self.mock_s3)

        mock_raise_error.assert_called_once_with(
            "Revision 11 not found for entity Q42", status_code=404
        )


if __name__ == "__main__":
    unittest.main()
