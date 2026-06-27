"""Unit tests for admin handler."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestAdminHandlerMethods:
    """Test AdminHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.mysql_client = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.admin import AdminHandler

        handler = AdminHandler(state=mock_state)
        return handler

    def test_list_entities(self, handler, mock_state):
        """Test list_entities returns result."""
        mock_state.mysql_client.entity_repository.list_entities_filtered.return_value = []

        result = handler.list_entities(entity_type="item", limit=10, offset=0)
        assert result is not None

    def test_list_entities_by_type(self, handler, mock_state):
        """Test list_entities_by_type returns result."""
        mock_state.mysql_client.list_entities_by_type.return_value = []

        result = handler.list_entities_by_type("item", limit=10, offset=0)
        assert result is not None

    def test_list_entities_mysql_not_initialized(self, mock_state):
        """Test list_entities raises 503 when mysql not initialized."""
        from models.rest_api.entitybase.v1.handlers.admin import AdminHandler

        mock_state.mysql_client = None
        handler = AdminHandler(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            handler.list_entities(entity_type="item")
        assert exc_info.value.status_code == 503

    def test_list_entities_no_filters(self, handler):
        """Test list_entities raises 400 when no filters provided."""
        with pytest.raises(HTTPException) as exc_info:
            handler.list_entities()
        assert exc_info.value.status_code == 400

    def test_list_entities_invalid_status(self, handler):
        """Test list_entities raises 400 for invalid status."""
        with pytest.raises(HTTPException) as exc_info:
            handler.list_entities(status="invalid_status")
        assert exc_info.value.status_code == 400

    def test_list_entities_by_type_mysql_not_initialized(self, mock_state):
        """Test list_entities_by_type raises 503 when mysql not initialized."""
        from models.rest_api.entitybase.v1.handlers.admin import AdminHandler

        mock_state.mysql_client = None
        handler = AdminHandler(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            handler.list_entities_by_type("item")
        assert exc_info.value.status_code == 503
