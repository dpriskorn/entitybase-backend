"""Unit tests for add_property endpoint."""

import unittest
from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler
from models.rest_api.entitybase.v1.request.entity.add_property import AddPropertyRequest


@pytest.mark.asyncio
class TestAddProperty(unittest.TestCase):
    """Unit tests for add_property functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = EntityHandler(state=State())
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_validator = MagicMock()

    async def test_invalid_property_id_format(self) -> None:
        """Test invalid property ID format."""
        request = AddPropertyRequest(claims=[], edit_summary="test")
        result = await self.handler.add_property(
            "Q1", "invalid", request, self.mock_vitess, self.mock_s3
        )
        self.assertFalse(result.success)
        self.assertIn("Invalid property ID format", result.error)

    @patch("models.rest_api.entitybase.v1.handlers.entity.handler.EntityReadHandler")
    async def test_property_does_not_exist(self, mock_read_handler_class) -> None:
        """Test property does not exist."""
        mock_read_handler = MagicMock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.side_effect = Exception("Not found")

        request = AddPropertyRequest(claims=[], edit_summary="test")
        result = await self.handler.add_property(
            "Q1", "P1", request, self.mock_vitess, self.mock_s3
        )
        self.assertFalse(result.success)
        self.assertIn("Property does not exist", result.error)

    @patch("models.rest_api.entitybase.v1.handlers.entity.handler.EntityReadHandler")
    async def test_entity_is_not_property(self, mock_read_handler_class) -> None:
        """Test entity exists but is not a property."""
        mock_read_handler = MagicMock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_property_response = MagicMock()
        mock_property_response.entity_type = "item"
        mock_read_handler.get_entity.side_effect = [
            mock_property_response,
            Exception("Entity not found"),
        ]

        request = AddPropertyRequest(claims=[], edit_summary="test")
        result = await self.handler.add_property(
            "Q1", "P1", request, self.mock_vitess, self.mock_s3
        )
        self.assertFalse(result.success)
        self.assertIn("Entity is not a property", result.error)


if __name__ == "__main__":
    unittest.main()
