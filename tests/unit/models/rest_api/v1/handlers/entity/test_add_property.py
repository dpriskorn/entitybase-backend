"""Unit tests for add_property endpoint."""

import unittest
from unittest.mock import MagicMock, patch
from models.rest_api.entitybase.handlers.entity.base import EntityHandler
from models.rest_api.entitybase.request.entity.add_property import AddPropertyRequest
from models.common import OperationResult
from models.rest_api.entitybase.response import EntityResponse, EntityState


class TestAddProperty(unittest.TestCase):
    """Unit tests for add_property functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = EntityHandler()
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_validator = MagicMock()

    def test_invalid_property_id_format(self):
        """Test invalid property ID format."""
        request = AddPropertyRequest(claims=[], edit_summary="test")
        result = self.handler.add_property("Q1", "invalid", request, self.mock_vitess, self.mock_s3)
        self.assertFalse(result.success)
        self.assertIn("Invalid property ID format", result.error)

    @patch('models.rest_api.entitybase.handlers.entity.base.EntityReadHandler')
    def test_property_does_not_exist(self, mock_read_handler_class):
        """Test property does not exist."""
        mock_read_handler = MagicMock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.side_effect = Exception("Not found")
        
        request = AddPropertyRequest(claims=[], edit_summary="test")
        result = self.handler.add_property("Q1", "P1", request, self.mock_vitess, self.mock_s3)
        self.assertFalse(result.success)
        self.assertIn("Property does not exist", result.error)

    @patch('models.rest_api.entitybase.handlers.entity.base.EntityReadHandler')
    def test_entity_is_not_property(self, mock_read_handler_class):
        """Test entity exists but is not a property."""
        mock_read_handler = MagicMock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_property_response = MagicMock()
        mock_property_response.entity_type = "item"
        mock_read_handler.get_entity.side_effect = [mock_property_response, Exception("Entity not found")]
        
        request = AddPropertyRequest(claims=[], edit_summary="test")
        result = self.handler.add_property("Q1", "P1", request, self.mock_vitess, self.mock_s3)
        self.assertFalse(result.success)
        self.assertIn("Entity is not a property", result.error)

    @patch('models.rest_api.entitybase.handlers.entity.base.EntityReadHandler')
    @patch.object(EntityHandler, '_create_and_store_revision')
    @patch.object(EntityHandler, 'process_statements')
    def test_successful_add_property(self, mock_process, mock_create, mock_read_handler_class):
        """Test successful property addition."""
        mock_read_handler = MagicMock()
        mock_read_handler_class.return_value = mock_read_handler
        
        # Property exists
        mock_property_response = MagicMock()
        mock_property_response.entity_type = "property"
        mock_read_handler.get_entity.side_effect = [mock_property_response, mock_entity_response]
        
        # Entity exists
        mock_entity_response = MagicMock()
        mock_entity_response.revision_id = 100
        mock_entity_response.entity_data = {"claims": {}}
        mock_entity_response.entity_type = "item"
        mock_entity_response.state = EntityState()
        
        # Process statements
        mock_hash_result = MagicMock()
        mock_process.return_value = mock_hash_result
        
        # Create revision
        mock_revision_result = MagicMock()
        mock_revision_result.success = True
        mock_revision_result.data.rev_id = 101
        mock_create.return_value = mock_revision_result
        
        request = AddPropertyRequest(
            claims=[{"mainsnak": {"property": "P1", "value": "test"}}],
            edit_summary="Added claim"
        )
        
        result = self.handler.add_property("Q1", "P1", request, self.mock_vitess, self.mock_s3)
        
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"revision_id": 101})
        mock_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()