"""Unit tests for ItemCreateHandler in item.py."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler


class TestItemCreateHandlerResolveEntityId:
    """Tests for ItemCreateHandler._resolve_entity_id."""

    def _make_request(self, entity_id: str | None = None) -> MagicMock:
        request = MagicMock(spec=EntityCreateRequest)
        request.id = entity_id
        return request

    def test_resolve_entity_id_with_explicit_id_not_exists(self) -> None:
        mock_state = MagicMock()
        mock_state.mysql_client.id_resolver.entity_exists.return_value = False
        handler = ItemCreateHandler(state=mock_state)

        request = self._make_request("Q42")
        result = handler._resolve_entity_id(request)

        assert result == "Q42"
        assert request.id == "Q42"
        mock_state.mysql_client.id_resolver.entity_exists.assert_called_once_with("Q42")

    def test_resolve_entity_id_with_explicit_id_exists(self) -> None:
        mock_state = MagicMock()
        mock_state.mysql_client.id_resolver.entity_exists.return_value = True
        handler = ItemCreateHandler(state=mock_state)

        request = self._make_request("Q42")
        with pytest.raises(HTTPException) as exc_info:
            handler._resolve_entity_id(request)
        assert exc_info.value.status_code == 409

    def test_resolve_entity_id_auto_assign_success(self) -> None:
        mock_state = MagicMock()
        handler = ItemCreateHandler(state=mock_state)
        mock_enum = MagicMock()
        mock_enum.get_next_entity_id.return_value = "Q999"
        handler.enumeration_service = mock_enum

        request = self._make_request(None)
        result = handler._resolve_entity_id(request)

        assert result == "Q999"
        assert request.id == "Q999"
        mock_enum.get_next_entity_id.assert_called_once_with("item")

    def test_resolve_entity_id_auto_assign_no_enum_service(self) -> None:
        mock_state = MagicMock()
        handler = ItemCreateHandler(state=mock_state)
        handler.enumeration_service = None

        request = self._make_request(None)
        with pytest.raises(HTTPException) as exc_info:
            handler._resolve_entity_id(request)
        assert exc_info.value.status_code == 500


class TestItemCreateHandlerPrepareRequestData:
    """Tests for ItemCreateHandler._prepare_request_data."""

    def test_prepare_request_data_copies_and_sets_id(self) -> None:
        request = MagicMock(spec=EntityCreateRequest)
        request.id = None
        request.data = MagicMock()
        mock_data_copy = MagicMock()
        request.data.model_copy.return_value = mock_data_copy
        mock_data_copy.id = "Q42"
        mock_data_copy.model_dump.return_value = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": "test"},
        }

        result = ItemCreateHandler._prepare_request_data(request, "Q42")

        assert result.id == "Q42"


class TestItemCreateHandlerExecuteCreationTransaction:
    """Tests for ItemCreateHandler._execute_creation_transaction."""

    @pytest.mark.asyncio
    async def test_execute_creation_transaction_success(self) -> None:
        from models.data.rest_api.v1.entitybase.response import StatementHashResult
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            CreationTransactionContext,
        )

        mock_tx = MagicMock()
        mock_tx.process_statements.return_value = StatementHashResult(
            statements=[], labels={}, descriptions={}, aliases={}, sitelinks={}
        )
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 1
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event = AsyncMock()
        mock_tx.commit = MagicMock()

        mock_ctx = MagicMock(spec=CreationTransactionContext)
        mock_ctx.tx = mock_tx
        mock_ctx.entity_id = "Q42"
        mock_ctx.request_data = MagicMock()
        mock_ctx.edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        mock_ctx.validator = None

        result = await ItemCreateHandler._execute_creation_transaction(mock_ctx)

        assert result == mock_response
        mock_tx.register_entity.assert_called_once_with("Q42")
        mock_tx.process_statements.assert_called_once()
        mock_tx.create_revision.assert_awaited_once()
        mock_tx.publish_event.assert_awaited_once()
        mock_tx.commit.assert_called_once()


class TestItemCreateHandlerCreateEntity:
    """Tests for ItemCreateHandler.create_entity orchestrator."""

    @pytest.mark.asyncio
    async def test_create_entity_with_explicit_id_success(self) -> None:
        from models.data.rest_api.v1.entitybase.response import StatementHashResult

        mock_state = MagicMock()
        mock_state.mysql_client.id_resolver.entity_exists.return_value = False
        handler = ItemCreateHandler(state=mock_state)

        mock_tx = MagicMock()
        mock_tx.process_statements.return_value = StatementHashResult(
            statements=[], labels={}, descriptions={}, aliases={}, sitelinks={}
        )
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 1
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event = AsyncMock()
        mock_tx.commit = MagicMock()

        request = MagicMock(spec=EntityCreateRequest)
        request.id = "Q42"
        request.data = MagicMock()
        mock_data_copy = MagicMock()
        request.data.model_copy.return_value = mock_data_copy

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.item.CreationTransaction",
            return_value=mock_tx,
        ):
            result = await handler.create_entity(request, edit_headers)

        assert result == mock_response
        mock_tx.register_entity.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    async def test_create_entity_with_auto_assign_id_success(self) -> None:
        from models.data.rest_api.v1.entitybase.response import StatementHashResult

        mock_state = MagicMock()
        mock_state.mysql_client.id_resolver.entity_exists.return_value = False
        handler = ItemCreateHandler(state=mock_state)
        mock_enum = MagicMock()
        mock_enum.get_next_entity_id.return_value = "Q999"
        mock_enum.confirm_id_usage = MagicMock()
        handler.enumeration_service = mock_enum

        mock_tx = MagicMock()
        mock_tx.process_statements.return_value = StatementHashResult(
            statements=[], labels={}, descriptions={}, aliases={}, sitelinks={}
        )
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 1
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event = AsyncMock()
        mock_tx.commit = MagicMock()

        request = MagicMock(spec=EntityCreateRequest)
        request.id = None
        request.data = MagicMock()
        mock_data_copy = MagicMock()
        request.data.model_copy.return_value = mock_data_copy

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.item.CreationTransaction",
            return_value=mock_tx,
        ):
            result = await handler.create_entity(request, edit_headers)

        assert result == mock_response
        mock_enum.confirm_id_usage.assert_called_once_with("Q999")

    @pytest.mark.asyncio
    async def test_create_entity_rollback_on_exception(self) -> None:
        mock_state = MagicMock()
        mock_state.mysql_client.id_resolver.entity_exists.return_value = False
        handler = ItemCreateHandler(state=mock_state)

        mock_tx = MagicMock()
        mock_tx.process_statements.side_effect = Exception("DB error")
        mock_tx.rollback = MagicMock()

        request = MagicMock(spec=EntityCreateRequest)
        request.id = "Q42"
        request.data = MagicMock()
        mock_data_copy = MagicMock()
        request.data.model_copy.return_value = mock_data_copy

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.item.CreationTransaction",
            return_value=mock_tx,
        ):
            with pytest.raises(Exception, match="DB error"):
                await handler.create_entity(request, edit_headers)

        mock_tx.rollback.assert_called_once()
