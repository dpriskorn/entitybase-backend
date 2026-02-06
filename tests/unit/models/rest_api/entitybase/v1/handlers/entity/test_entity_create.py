"""Unit tests for create."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.data.infrastructure.s3.enums import EntityType, EditType
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.rest_api.entitybase.v1.handlers.entity.create import EntityCreateHandler
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders


class TestEntityCreateHandler:
    """Unit tests for EntityCreateHandler."""





    @pytest.mark.asyncio
    async def test_create_entity_exists(self) -> None:
        """Test creating an entity that already exists."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = True

        handler = EntityCreateHandler(state=mock_state)

        request = EntityCreateRequest(
            type="item",
            id="Q42",
            labels={"en": {"value": "Test Entity"}}
        )

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test creation")
        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request, edit_headers=edit_headers)

        mock_vitess.entity_exists.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    async def test_create_entity_deleted(self) -> None:
        """Test creating an entity that is deleted."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = True

        handler = EntityCreateHandler(state=mock_state)

        request = EntityCreateRequest(
            type="item",
            id="Q42",
            labels={"en": {"value": "Test Entity"}}
        )

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test creation")
        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request, edit_headers=edit_headers)

    @pytest.mark.asyncio
    async def test_create_entity_missing_id_no_auto_assign(self) -> None:
        """Test entity creation with missing ID and no auto-assign."""
        mock_state = MagicMock()

        handler = EntityCreateHandler(state=mock_state)

        request = EntityCreateRequest(
            type="item",
            labels={"en": {"value": "Test Entity"}}
        )

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test creation")
        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request, edit_headers=edit_headers)

    @pytest.mark.asyncio
    async def test_create_entity_auto_assign_no_enumeration_service(self) -> None:
        """Test entity creation with auto-assign but no enumeration service."""
        mock_state = MagicMock()

        handler = EntityCreateHandler(state=mock_state, enumeration_service=None)

        request = EntityCreateRequest(
            type="item",
            labels={"en": {"value": "Test Entity"}}
        )

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test creation")
        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request, edit_headers=edit_headers, auto_assign_id=True)





    @pytest.mark.asyncio
    async def test_create_entity_with_validator(self) -> None:
        """Test entity creation with custom validator."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.register_entity.return_value = None

        mock_validator = MagicMock()
        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"id": "Q42", "type": "item"},
            hash=123456789,
            created_at="2023-01-01T12:00:00Z"
        )
        mock_response = EntityResponse(
            id="Q42",
            rev_id=12345,
            data=s3_revision_data
        )

        handler = EntityCreateHandler(state=mock_state)

        with patch('models.rest_api.entitybase.v1.handlers.entity.handler.EntityHandler.process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                id="Q42",
                labels={"en": {"value": "Test Entity"}}
            )

            edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test creation")
            result = await handler.create_entity(request, edit_headers=edit_headers, validator=mock_validator)

            assert result.id == "Q42"
            # Verify validator was passed to process method
            mock_process.assert_called_once()
            ctx = mock_process.call_args[0][0]
            assert ctx.validator == mock_validator


