"""Unit tests for PropertyCreateHandler in property/create.py."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.property.create import (
    PropertyCreateHandler,
)


class TestPropertyCreateHandler:
    """Tests for PropertyCreateHandler."""

    @pytest.mark.asyncio
    async def test_create_property_logs_debug_message(self) -> None:
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 1
        mock_response.entity_id = "P42"

        mock_state = MagicMock()
        mock_state.vitess_client.entity_exists.return_value = False
        mock_state.vitess_client.register_entity.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=True)
        )

        handler = PropertyCreateHandler(state=mock_state)

        request = MagicMock(spec=EntityCreateRequest)
        request.id = "P42"
        request.type = "property"
        request.data = MagicMock()
        request.data.model_dump.return_value = {}
        request.edit_type = "create"
        request.is_mass_edit = False

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.create.EntityCreateHandler.process_entity_revision_new",
            new_callable=AsyncMock,
        ) as mock_process:
            mock_process.return_value = mock_response
            result = await handler.create_entity(request, edit_headers)

        assert result == mock_response
        mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_property_auto_assign_id_when_no_id_provided(self) -> None:
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 1
        mock_response.entity_id = "P999"

        mock_state = MagicMock()
        mock_state.vitess_client.entity_exists.return_value = False
        mock_state.vitess_client.register_entity.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=True)
        )

        handler = PropertyCreateHandler(state=mock_state)
        handler.enumeration_service = MagicMock()
        handler.enumeration_service.get_next_entity_id.return_value = "P999"

        request = MagicMock(spec=EntityCreateRequest)
        request.id = None
        request.type = "property"
        request.data = MagicMock()
        request.data.model_dump.return_value = {}
        request.edit_type = "create"
        request.is_mass_edit = False

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.create.EntityCreateHandler.process_entity_revision_new",
            new_callable=AsyncMock,
        ) as mock_process:
            mock_process.return_value = mock_response
            result = await handler.create_entity(request, edit_headers)

        assert result == mock_response
        mock_process.assert_called_once()
        handler.enumeration_service.get_next_entity_id.assert_called_once_with(
            "property"
        )
