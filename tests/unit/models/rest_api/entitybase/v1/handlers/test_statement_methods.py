"""Unit tests for statement handler methods."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


class TestStatementHandlerMethods:
    """Test StatementHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        state.s3_client = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_statement_not_found(self, handler, mock_state):
        """Test get_statement raises 404 when not found."""
        from models.infrastructure.s3.exceptions import S3NotFoundError

        mock_state.s3_client.read_statement.side_effect = S3NotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            handler.get_statement(999999)

        assert exc_info.value.status_code == 404

    def test_get_entity_properties_not_found(self, handler, mock_state):
        """Test get_entity_properties raises 404 for nonexistent entity."""
        mock_state.vitess_client.entity_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_properties("Q99999")

        assert exc_info.value.status_code == 404

    def test_get_entity_properties_no_revisions(self, handler, mock_state):
        """Test get_entity_properties raises 404 when entity has no revisions."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 0

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_properties("Q42")

        assert exc_info.value.status_code == 404

    def test_get_entity_property_counts_not_found(self, handler, mock_state):
        """Test get_entity_property_counts raises 404 for nonexistent entity."""
        mock_state.vitess_client.entity_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_property_counts("Q99999")

        assert exc_info.value.status_code == 404

    def test_get_entity_property_hashes_invalid_entity(self, handler, mock_state):
        """Test get_entity_property_hashes raises 404 for invalid entity."""
        mock_state.vitess_client.entity_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_property_hashes("Q99999", "P31")

        assert exc_info.value.status_code == 404

    def test_cleanup_orphaned_statements(self, handler, mock_state):
        """Test cleanup_orphaned_statements returns counts."""
        from models.data.rest_api.v1.entitybase.request import CleanupOrphanedRequest

        mock_request = CleanupOrphanedRequest(older_than_days=30, limit=100)
        mock_state.vitess_client.get_orphaned_statements.return_value = []

        result = handler.cleanup_orphaned_statements(request=mock_request)

        assert result is not None

    def test_get_most_used_statements(self, handler, mock_state):
        """Test get_most_used_statements returns results."""
        mock_state.vitess_client.statement_repository.get_most_used.return_value = []

        result = handler.get_most_used_statements(limit=10, min_ref_count=2)

        assert result is not None
        assert hasattr(result, "statements")
