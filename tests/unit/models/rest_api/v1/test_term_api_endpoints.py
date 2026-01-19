import unittest
from unittest.mock import Mock, patch


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

        result = get_item_label("Q42", "en", self.mock_request)

        self.assertEqual(result, {"language": "en", "value": "Douglas Adams"})
        mock_handler.get_entity.assert_called_once()

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_description_success(self, mock_handler_class) -> None:
        """Test entitybase GET item description"""
        from models.rest_api.entitybase.versions.v1.items import get_item_description

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.get_entity.return_value = self.mock_entity_response

        result = get_item_description("Q42", "en", self.mock_request)

        self.assertEqual(
            result, {"language": "en", "value": "English writer and comedian"}
        )

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_aliases_success(self, mock_handler_class) -> None:
        """Test entitybase GET item aliases"""
        from models.rest_api.entitybase.versions.v1.items import get_item_aliases_for_language

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.get_entity.return_value = self.mock_entity_response

        result = get_item_aliases_for_language("Q42", "en", self.mock_request)

        expected = [
            {"language": "en", "value": "DNA"},
            {"language": "en", "value": "42"},
        ]
        self.assertEqual(result, expected)

    # ===== ENTITYBASE PUT ENDPOINTS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_put_item_label_success(
        self, mock_read_handler_class, mock_update_handler_class
    ):
        """Test entitybase PUT item label"""
        from models.rest_api.entitybase.versions.v1.items import update_item_label

        mock_read_handler = Mock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.return_value = self.mock_entity_response

        mock_update_handler = Mock()
        mock_update_handler_class.return_value = mock_update_handler
        mock_update_result = Mock()
        mock_update_handler.update_entity.return_value = mock_update_result

        update_data = {"value": "Updated Label"}
        result = update_item_label("Q42", "en", update_data, self.mock_request)

        self.assertEqual(result, mock_update_result)
        mock_update_handler.update_entity.assert_called_once()

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_put_item_description_success(
        self, mock_read_handler_class, mock_update_handler_class
    ):
        """Test entitybase PUT item description"""
        from models.rest_api.entitybase.versions.v1.items import update_item_description

        mock_read_handler = Mock()
        mock_read_handler_class.return_value = mock_read_handler
        mock_read_handler.get_entity.return_value = self.mock_entity_response

        mock_update_handler = Mock()
        mock_update_handler_class.return_value = mock_update_handler
        mock_update_result = Mock()
        mock_update_handler.update_entity.return_value = mock_update_result

        update_data = {"description": "Updated description"}
        result = update_item_description("Q42", "en", update_data, self.mock_request)

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
    def test_entitybase_delete_item_label_success(
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

        result = delete_item_label("Q42", "en", self.mock_request)

        self.assertEqual(result, mock_update_result)

    @patch("models.rest_api.entitybase.versions.v1.items.EntityUpdateHandler")
    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_delete_item_description_success(
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

        result = delete_item_description("Q42", "en", self.mock_request)

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

    @unittest.skip("Wikibase redirect endpoints are not implemented")
    def test_wikibase_put_item_label_redirect(self) -> None:
        """Test Wikibase PUT item label redirects"""
        # from models.rest_api.wikibase.v1.entity.items import set_item_label
        # from fastapi.responses import RedirectResponse
        # result = set_item_label("Q42", "en")
        # self.assertIsInstance(result, RedirectResponse)
        # self.assertEqual(result.status_code, 307)
        # self.assertEqual(result.headers["location"], "/entitybase/v1/entities/items/Q42/labels/en")
        self.skipTest("Wikibase redirect functionality not implemented")

    @unittest.skip("Wikibase redirect endpoints are not implemented")
    def test_wikibase_patch_item_aliases_redirect(self) -> None:
        """Test Wikibase PATCH item aliases redirects"""
        # from models.rest_api.wikibase.v1.entity.items import (
        #     patch_item_aliases_for_language,
        # )
        # from fastapi.responses import RedirectResponse
        # result = patch_item_aliases_for_language("Q42", "en", {})
        # self.assertIsInstance(result, RedirectResponse)
        # self.assertEqual(result.status_code, 307)
        # self.assertEqual(result.headers["location"], "/entitybase/v1/entities/items/Q42/aliases/en")
        self.skipTest("Wikibase redirect functionality not implemented")

    @unittest.skip("Wikibase redirect endpoints are not implemented")
    def test_wikibase_delete_item_label_redirect(self) -> None:
        """Test Wikibase DELETE item label redirects"""
        # from models.rest_api.wikibase.v1.entity.items import delete_item_label
        # from fastapi.responses import RedirectResponse
        # result = delete_item_label("Q42", "en")
        # self.assertIsInstance(result, RedirectResponse)
        # self.assertEqual(result.status_code, 307)
        # self.assertEqual(result.headers["location"], "/entitybase/v1/entities/items/Q42/labels/en")
        self.skipTest("Wikibase redirect functionality not implemented")

    # ===== ERROR SCENARIOS =====

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_get_item_label_not_found(self, mock_handler_class) -> None:
        """Test entitybase GET item label - term not found"""
        from models.rest_api.entitybase.versions.v1.items import get_item_label
        from fastapi import HTTPException

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler

        # Entity exists but term doesn't
        mock_response = Mock()
        mock_response.data = {"labels": {}}  # No labels
        mock_handler.get_entity.return_value = mock_response

        with self.assertRaises(HTTPException) as context:
            get_item_label("Q42", "en", self.mock_request)

        self.assertEqual(context.exception.status_code, 404)

    @patch("models.rest_api.entitybase.versions.v1.items.EntityReadHandler")
    def test_entitybase_put_item_label_missing_value(self, mock_handler_class) -> None:
        """Test entitybase PUT item label - missing value field"""
        from models.rest_api.entitybase.versions.v1.items import update_item_label
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as context:
            update_item_label("Q42", "en", {}, self.mock_request)  # Empty data

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
            update_item_description("Q42", "en", {}, self.mock_request)  # Empty data

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Missing 'description' field", str(context.exception.detail))


if __name__ == "__main__":
    unittest.main()
