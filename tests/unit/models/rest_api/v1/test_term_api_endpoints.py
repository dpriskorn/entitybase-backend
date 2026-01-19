import unittest
import asyncio
from unittest.mock import Mock, patch

import pytest


class TestTermAPIEndpoints(unittest.TestCase):
    """Comprehensive tests for all term API endpoints"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_request = Mock()
        self.mock_clients = Mock()
        self.mock_request.app.state.clients = self.mock_clients

        # Mock common response data
        self.mock_entity_response = Mock()
        self.mock_entity_response.data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {
                "en": {"language": "en", "value": "English writer and comedian"}
            },
            "aliases": {
                "en": [
                    {"language": "en", "value": "DNA"},
                    {"language": "en", "value": "42"},
                ]
            },
        }

    # ===== ENTITYBASE GET ENDPOINTS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_label_success(self, mock_handler_class) -> None:
        """Test entitybase GET item label"""
        from models.rest_api.entitybase.versions.v1.items import get_item_label

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.get_entity.return_value = self.mock_entity_response

        result = asyncio.run(get_item_label("Q42", "en", self.mock_request))

        self.assertEqual(result, {"language": "en", "value": "Douglas Adams"})
        mock_handler.get_entity.assert_called_once()

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_description_success(self, mock_handler_class) -> None:
        """Test entitybase GET item description"""
        from models.rest_api.entitybase.versions.v1.items import get_item_description

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.get_entity.return_value = self.mock_entity_response

        result = asyncio.run(get_item_description("Q42", "en", self.mock_request))

        self.assertEqual(
            result, {"language": "en", "value": "English mathematician and writer"}
        )

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_aliases_success(self, mock_handler_class) -> None:
        """Test entitybase GET item aliases"""
        from models.rest_api.entitybase.versions.v1.items import get_item_aliases

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.get_entity.return_value = self.mock_entity_response

        result = asyncio.run(get_item_aliases("Q42", "en", self.mock_request))

        expected = [{"language": "en", "value": "alias1"}, {"language": "en", "value": "alias2"}]
        self.assertEqual(result, expected)

    # ===== ENTITYBASE PUT ENDPOINTS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    def test_entitybase_delete_item_label_success(
        self, mock_handler_class
    ):
        """Test entitybase DELETE item label"""
        from models.rest_api.entitybase.versions.v1.items import delete_item_label

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_update_result = Mock()
        mock_handler.update_entity.return_value = mock_update_result

        result = asyncio.run(delete_item_label("Q42", "en", self.mock_request))

        self.assertEqual(result, mock_update_result)
        mock_update_handler.update_entity.assert_called_once()

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    def test_entitybase_delete_item_description_success(
        self, mock_handler_class
    ):
        """Test entitybase DELETE item description"""
        from models.rest_api.entitybase.versions.v1.items import delete_item_description

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_update_result = Mock()
        mock_handler.update_entity.return_value = mock_update_result

        result = asyncio.run(delete_item_description("Q42", "en", self.mock_request))

        self.assertEqual(result, mock_update_result)

    # ===== ENTITYBASE PATCH ENDPOINTS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_patch_item_aliases_success(
        self, mock_read_handler_class, mock_update_handler_class
    ):
        """Test entitybase PATCH item aliases"""
        from models.rest_api.entitybase.versions.v1.items import patch_item_aliases_for_language

        mock_read_handler = Mock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.return_value = self.mock_entity_response

        mock_update_handler = Mock()
        mock_update_handler_class.return_value = mock_update_handler
        mock_update_result = Mock()
        mock_update_handler.update_entity.return_value = mock_update_result

        patch_data = {"patch": [{"op": "add", "path": "/-", "value": "new_alias"}]}
        result = patch_item_aliases_for_language(
            "Q42", "en", patch_data, self.mock_request
        )

        self.assertEqual(result, mock_update_result)

    # ===== ENTITYBASE DELETE ENDPOINTS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    @pytest.mark.asyncio
    async def test_entitybase_delete_item_label_success(
        self, mock_read_handler_class, mock_update_handler_class
    ):
        """Test entitybase DELETE item label"""
        from models.rest_api.entitybase.versions.v1.items import delete_item_label

        mock_read_handler = Mock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.return_value = self.mock_entity_response

        mock_update_handler = Mock()
        mock_update_handler_class.return_value = mock_update_handler
        mock_update_result = Mock()
        mock_update_handler.update_entity.return_value = mock_update_result

        result = await delete_item_label("Q42", "en", self.mock_request)

        self.assertEqual(result, mock_update_result)

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    @pytest.mark.asyncio
    async def test_entitybase_delete_item_description_success(
        self, mock_read_handler_class, mock_update_handler_class
    ):
        """Test entitybase DELETE item description"""
        from models.rest_api.entitybase.versions.v1.items import delete_item_description

        mock_read_handler = Mock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.return_value = self.mock_entity_response

        mock_update_handler = Mock()
        mock_update_handler_class.return_value = mock_update_handler
        mock_update_result = Mock()
        mock_update_handler.update_entity.return_value = mock_update_result

        result = await delete_item_description("Q42", "en", self.mock_request)

        self.assertEqual(result, mock_update_result)

    # ===== WIKIBASE REDIRECT ENDPOINTS =====

    def test_wikibase_get_item_label_redirect(self) -> None:
        """Test Wikibase GET item label redirects"""
        from models.rest_api.entitybase.versions.v1.items import get_item_label
        from fastapi.responses import RedirectResponse

        result = get_item_label("Q42", "en")

        self.assertIsInstance(result, RedirectResponse)
        self.assertEqual(result.status_code, 307)
        self.assertEqual(
            result.headers["location"], "/entitybase/v1/entities/items/Q42/labels/en"
        )

    # ===== ERROR SCENARIOS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_label_not_found(self, mock_handler_class) -> None:
        """Test entitybase GET item label not found"""
        from models.rest_api.entitybase.versions.v1.items import get_item_label
        from fastapi import HTTPException

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.get_entity.side_effect = HTTPException(status_code=404, detail="Label not found")

        with self.assertRaises(HTTPException) as context:
            asyncio.run(get_item_label("Q42", "en", self.mock_request))
        self.assertEqual(context.exception.status_code, 404)

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_put_item_label_missing_value(self, mock_handler_class) -> None:
        """Test entitybase PUT item label - missing value field"""
        from models.rest_api.entitybase.versions.v1.items import update_item_label
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as context:
            asyncio.run(update_item_label("Q42", "en", {}, self.mock_request))  # Empty data

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Missing 'value' field", str(context.exception.detail))

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_put_item_description_missing_description(
        self, mock_handler_class
    ):
        """Test entitybase PUT item description - missing description field"""
        from models.rest_api.entitybase.versions.v1.items import update_item_description
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as context:
            asyncio.run(update_item_description("Q42", "en", {}, self.mock_request))  # Empty data

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Missing 'description' field", str(context.exception.detail))


if __name__ == "__main__":
    unittest.main()
