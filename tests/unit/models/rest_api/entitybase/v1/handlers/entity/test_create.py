"""Unit tests for create."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.data.infrastructure.s3.enums import EntityType, EditType
from models.rest_api.entitybase.v1.handlers.entity.create import EntityCreateHandler
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse


class TestEntityCreateHandler:
    """Unit tests for EntityCreateHandler."""

    @pytest.mark.asyncio
    async def test_create_entity_success_manual_id(self) -> None:
        """Test successful entity creation with manually assigned ID."""
        # Mock state and clients
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        mock_vitess.user_repository = mock_user_repo

        # Mock Vitess responses
        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.register_entity.return_value = None
        mock_user_repo.log_user_activity.return_value = MagicMock(success=True)

        # Mock the process_entity_revision_new method
        mock_response = EntityResponse(
            id="Q42",
            rev_id=12345,
            data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )

        handler = EntityCreateHandler(state=mock_state)

        with patch.object(handler, 'process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                id="Q42",
                labels={"en": {"value": "Test Entity"}},
                edit_summary="Test creation"
            )

            result = await handler.create_entity(request, user_id=123)

            assert isinstance(result, EntityResponse)
            assert result.id == "Q42"
            assert result.revision_id == 12345

            # Verify method calls
            mock_vitess.entity_exists.assert_called_once_with("Q42")
            mock_vitess.register_entity.assert_called_once_with("Q42")
            mock_vitess.is_entity_deleted.assert_called_once_with("Q42")

            mock_process.assert_called_once()
            call_args = mock_process.call_args
            assert call_args[1]["entity_id"] == "Q42"
            assert call_args[1]["entity_type"] == EntityType.ITEM
            assert call_args[1]["is_creation"] is True

            # Verify user activity logging
            mock_user_repo.log_user_activity.assert_called_once()
            activity_call = mock_user_repo.log_user_activity.call_args
            assert activity_call[1]["user_id"] == 123
            assert activity_call[1]["entity_id"] == "Q42"
            assert activity_call[1]["revision_id"] == 12345

    @pytest.mark.asyncio
    async def test_create_entity_success_auto_id(self) -> None:
        """Test successful entity creation with auto-assigned ID."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_enum_service = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        # Mock enumeration service
        mock_enum_service.get_next_entity_id.return_value = "Q100"

        # Mock Vitess responses
        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.register_entity.return_value = None

        # Mock response
        mock_response = EntityResponse(
            id="Q100",
            rev_id=12345,
            data={"id": "Q100", "type": "item"},
            state=MagicMock()
        )

        handler = EntityCreateHandler(state=mock_state, enumeration_service=mock_enum_service)

        with patch.object(handler, 'process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                labels={"en": {"value": "Test Entity"}},
                edit_summary="Test creation"
            )

            result = await handler.create_entity(request, auto_assign_id=True)

            assert result.id == "Q100"
            # Verify ID was assigned to request
            assert request.id == "Q100"

            mock_enum_service.get_next_entity_id.assert_called_once_with("item")

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
            labels={"en": {"value": "Test Entity"}},
            edit_summary="Test creation"
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request)

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
            labels={"en": {"value": "Test Entity"}},
            edit_summary="Test creation"
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request)

    @pytest.mark.asyncio
    async def test_create_entity_missing_id_no_auto_assign(self) -> None:
        """Test entity creation with missing ID and no auto-assign."""
        mock_state = MagicMock()

        handler = EntityCreateHandler(state=mock_state)

        request = EntityCreateRequest(
            type="item",
            labels={"en": {"value": "Test Entity"}},
            edit_summary="Test creation"
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request)

    @pytest.mark.asyncio
    async def test_create_entity_auto_assign_no_enumeration_service(self) -> None:
        """Test entity creation with auto-assign but no enumeration service."""
        mock_state = MagicMock()

        handler = EntityCreateHandler(state=mock_state, enumeration_service=None)

        request = EntityCreateRequest(
            type="item",
            labels={"en": {"value": "Test Entity"}},
            edit_summary="Test creation"
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.create_entity(request, auto_assign_id=True)

    @pytest.mark.asyncio
    async def test_create_entity_user_activity_logging_failure(self) -> None:
        """Test entity creation when user activity logging fails."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        mock_vitess.user_repository = mock_user_repo

        # Mock successful entity creation
        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.register_entity.return_value = None

        # Mock failed user activity logging
        mock_user_repo.log_user_activity.return_value = MagicMock(success=False, error="DB error")

        mock_response = EntityResponse(
            id="Q42",
            rev_id=12345,
            data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )

        handler = EntityCreateHandler(state=mock_state)

        with patch.object(handler, 'process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                id="Q42",
                labels={"en": {"value": "Test Entity"}},
                edit_summary="Test creation"
            )

            # Should still succeed despite logging failure
            result = await handler.create_entity(request, user_id=123)

            assert result.id == "Q42"
            mock_user_repo.log_user_activity.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_entity_no_user_activity_logging(self) -> None:
        """Test entity creation without user activity logging."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.register_entity.return_value = None

        mock_response = EntityResponse(
            id="Q42",
            rev_id=12345,
            data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )

        handler = EntityCreateHandler(state=mock_state)

        with patch.object(handler, 'process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                id="Q42",
                labels={"en": {"value": "Test Entity"}},
                edit_summary="Test creation"
            )

            result = await handler.create_entity(request)  # No user_id

            assert result.id == "Q42"
            # Should not attempt user activity logging
            mock_vitess.user_repository.log_user_activity.assert_not_called()

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
        mock_response = EntityResponse(
            id="Q42",
            rev_id=12345,
            data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )

        handler = EntityCreateHandler(state=mock_state)

        with patch.object(handler, 'process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                id="Q42",
                labels={"en": {"value": "Test Entity"}},
                edit_summary="Test creation"
            )

            result = await handler.create_entity(request, validator=mock_validator)

            assert result.id == "Q42"
            # Verify validator was passed to process method
            mock_process.assert_called_once()
            assert mock_process.call_args[1]["validator"] == mock_validator

    @pytest.mark.asyncio
    async def test_create_entity_mass_edit(self) -> None:
        """Test entity creation with mass edit flag."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = False
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.register_entity.return_value = None

        mock_response = EntityResponse(
            id="Q42",
            rev_id=12345,
            data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )

        handler = EntityCreateHandler(state=mock_state)

        with patch.object(handler, 'process_entity_revision_new', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_response

            request = EntityCreateRequest(
                type="item",
                id="Q42",
                labels={"en": {"value": "Test Entity"}},
                edit_summary="Test creation",
                        edit_type=EditType.MASS_EDIT
            )

            result = await handler.create_entity(request)

            assert result.id == "Q42"
            # Verify mass edit parameters are passed through
            mock_process.assert_called_once()
            call_kwargs = mock_process.call_args[1]
            assert call_kwargs["edit_type"] == "mass_edit"