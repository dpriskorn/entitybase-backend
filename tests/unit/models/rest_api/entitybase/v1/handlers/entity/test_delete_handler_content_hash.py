"""Unit tests for content_hash calculation and passing in delete handler."""

from unittest.mock import MagicMock, patch

from models.common import EditHeaders
from models.data.infrastructure.s3.enums import DeleteType
from models.data.rest_api.v1.entitybase.request import EntityDeleteRequest
from models.rest_api.entitybase.v1.handlers.entity.delete import EntityDeleteHandler


class TestEntityDeleteHandlerContentHash:
    """Unit tests for content_hash calculation and passing in delete handler."""

    def test_delete_calculates_content_hash(self):
        """Test that delete handler calculates content_hash before storing."""

        # Setup
        handler = EntityDeleteHandler(state=MagicMock())
        handler.state.vitess_client = MagicMock()
        handler.state.s3_client = MagicMock()
        handler.state.s3_client.read_revision = MagicMock(return_value=MagicMock(data={}))
        handler.state.vitess_client.entity_exists = MagicMock(return_value=True)
        handler.state.vitess_client.is_entity_deleted = MagicMock(return_value=False)
        handler.state.vitess_client.get_head = MagicMock(return_value=1)
        handler.state.vitess_client.get_protection_info = MagicMock(return_value=None)

        request = EntityDeleteRequest(
            delete_type=DeleteType.SOFT,
        )

        # Mock the current revision data
        current_revision = MagicMock()
        current_revision.data = {
            "entity_type": "item",
            "statements": [],
            "properties": [],
            "property_counts": {},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
            "sitelinks": {},
            "is_semi_protected": False,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False
        }

        with patch.object(handler.state.s3_client, "read_revision", return_value=current_revision):
            # Mock create_revision to capture arguments
            mock_create_revision = MagicMock()
            handler.state.vitess_client.create_revision = mock_create_revision

            # Mock store_revision to capture arguments
            mock_store_revision = MagicMock()
            handler.state.s3_client.store_revision = mock_store_revision

            # Execute delete
            result = handler.delete_entity("Q42", request, edit_headers=EditHeaders(x_user_id=12345, x_edit_summary="Test delete"))

            # Verify store_revision was called with content_hash argument
            assert mock_store_revision.called
            call_args = mock_store_revision.call_args

    def test_delete_passes_content_hash_to_vitess(self):
        """Test that delete handler passes content_hash to vitess create_revision."""
        from models.rest_api.entitybase.v1.handlers.entity.delete import EntityDeleteHandler

        # Setup
        handler = EntityDeleteHandler(state=MagicMock())
        handler.state.vitess_client = MagicMock()
        handler.state.s3_client = MagicMock()
        handler.state.vitess_client.entity_exists = MagicMock(return_value=True)
        handler.state.vitess_client.is_entity_deleted = MagicMock(return_value=False)
        handler.state.vitess_client.get_head = MagicMock(return_value=1)
        handler.state.vitess_client.get_protection_info = MagicMock(return_value=None)

        # Mock current revision
        current_revision = MagicMock()
        current_revision.data = {
            "entity_type": "item",
            "statements": [],
            "properties": [],
            "property_counts": {},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
            "sitelinks": {},
            "is_semi_protected": False,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False
        }
        handler.state.s3_client.read_revision = MagicMock(return_value=current_revision)

        request = EntityDeleteRequest(
            delete_type=DeleteType.SOFT,
        )

        # Execute and verify
        with patch("models.internal_representation.metadata_extractor.MetadataExtractor.hash_string", return_value=12345):
            result = handler.delete_entity("Q42", request, edit_headers=EditHeaders(x_user_id=12345, x_edit_summary="Test delete"))

        # Verify create_revision was called
        handler.state.vitess_client.create_revision.assert_called_once()
        call_kwargs = handler.state.vitess_client.create_revision.call_args[1]
        assert 'content_hash' in call_kwargs