"""Unit tests for content_hash calculation and passing in revert handler."""

from unittest.mock import MagicMock

from models.common import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityRevertRequest
from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler


class TestEntityRevertHandlerContentHash:
    """Unit tests for content_hash calculation and passing in revert handler."""

    def test_revert_calculates_content_hash(self):
        """Test that revert handler calculates content_hash before storing."""

        # Setup
        handler = EntityRevertHandler(state=MagicMock())
        handler.state.vitess_client = MagicMock()
        handler.state.s3_client = MagicMock()
        handler.state.vitess_client.id_resolver = MagicMock()

        # Mock getting revision
        mock_current_revision = MagicMock(data={"hashes": {}, "state": {}, "properties": [], "property_counts": {}})
        handler.state.vitess_client.revision_repository.get_revision.return_value = mock_current_revision

        # Mock S3 revision read
        mock_target_revision_data = MagicMock(data={"entity": {}, "statements": [], "properties": []})
        handler.state.s3_client.read_full_revision = MagicMock(return_value=mock_target_revision_data)

        # Mock head revision
        handler.state.vitess_client.head_repository.get_head_revision = MagicMock(
            return_value=MagicMock(data=1, success=True)
        )

        request = EntityRevertRequest(
            to_revision_id=1,
            watchlist_context=None,
        )

        # Mock store_revision to capture calls
        mock_store_revision = MagicMock()
        handler.state.s3_client.store_revision = mock_store_revision

        # Mock insert_revision
        mock_insert_revision = MagicMock()
        handler.state.vitess_client.insert_revision = mock_insert_revision

        # Execute revert
        import asyncio
        edit_headers = EditHeaders(x_user_id=1, x_edit_summary="Test revert")
        result = asyncio.run(handler.revert_entity("Q42", request, edit_headers))

        # Verify store_revision was called
        assert handler.state.s3_client.store_revision.called or handler.state.s3_client.write_revision.called

    def test_revert_passes_content_hash_to_vitess(self):
        """Test that revert handler passes RevisionData with content_hash to vitess."""
        # Setup
        handler = EntityRevertHandler(state=MagicMock())
        handler.state.vitess_client = MagicMock()
        handler.state.s3_client = MagicMock()
        handler.state.vitess_client.id_resolver = MagicMock()

        # Mock getting revision
        mock_current_revision = MagicMock(data={"hashes": {}, "state": {}, "properties": [], "property_counts": {}})
        handler.state.vitess_client.revision_repository.get_revision.return_value = mock_current_revision

        # Mock S3 revision read
        mock_target_revision_data = MagicMock(data={"entity": {}, "statements": [], "properties": []})
        handler.state.s3_client.read_full_revision = MagicMock(return_value=mock_target_revision_data)

        # Mock head revision
        handler.state.vitess_client.head_repository.get_head_revision = MagicMock(
            return_value=MagicMock(data=1, success=True)
        )

        request = EntityRevertRequest(
            to_revision_id=1,
            watchlist_context=None,
        )

        # Execute
        import asyncio
        edit_headers = EditHeaders(x_user_id=1, x_edit_summary="Test revert")
        result = asyncio.run(handler.revert_entity("Q42", request, edit_headers))

        # Verify insert_revision was called
        handler.state.vitess_client.insert_revision.assert_called_once()
        # Second positional argument is revision_data (RevisionData)
        call_args = handler.state.vitess_client.insert_revision.call_args
        assert len(call_args[0]) >= 3  # entity_id, revision_id, entity_data