"""Unit tests for update."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.request import EntityUpdateRequest
from models.rest_api.entitybase.v1.response import EntityResponse
from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.rest_api.utils import raise_validation_error


class TestEntityUpdateHandler:
    """Unit tests for EntityUpdateHandler."""

    @pytest.mark.asyncio
    async def test_update_entity_success(self) -> None:
        """Test successful entity update."""
        # Mock state and clients
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        mock_vitess.user_repository = mock_user_repo

        # Mock Vitess responses
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False
        mock_user_repo.log_user_activity.return_value = MagicMock(success=True)

        # Mock UpdateTransaction
        mock_tx = MagicMock()
        mock_tx.head_revision_id = 12344
        mock_tx.entity_id = "Q42"

        # Mock transaction methods
        mock_hash_result = MagicMock()
        mock_tx.process_statements.return_value = mock_hash_result

        mock_response = EntityResponse(
            id="Q42",
            revision_id=12345,
            entity_data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event.return_value = None

        handler = EntityUpdateHandler(state=mock_state)

        with patch("models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction") as mock_tx_class:
            mock_tx_class.return_value = mock_tx

            request = EntityUpdateRequest(
                type="item",
                data={"labels": {"en": {"value": "Updated Entity"}}},
                edit_summary="Test update"
            )

            result = await handler.update_entity("Q42", request, user_id=123)

            assert isinstance(result, EntityResponse)
            assert result.id == "Q42"
            assert result.revision_id == 12345

            # Verify validation checks
            mock_vitess.entity_exists.assert_called_once_with("Q42")
            mock_vitess.is_entity_deleted.assert_called_once_with("Q42")
            mock_vitess.is_entity_locked.assert_called_once_with("Q42")

            # Verify transaction usage
            mock_tx_class.assert_called_once_with(state=mock_state)
            assert mock_tx.entity_id == "Q42"
            mock_tx.get_head.assert_called_once()
            mock_tx.process_statements.assert_called_once_with("Q42", {"id": "Q42", "labels": {"en": {"value": "Updated Entity"}}}, None)

            # Verify revision creation
            mock_tx.create_revision.assert_called_once()
            create_call = mock_tx.create_revision.call_args
            assert create_call[1]["entity_id"] == "Q42"
            assert create_call[1]["new_revision_id"] == 12345
            assert create_call[1]["head_revision_id"] == 12344
            assert create_call[1]["entity_type"] == EntityType.item
            assert create_call[1]["is_creation"] is False

            # Verify event publishing
            mock_tx.publish_event.assert_called_once()
            event_call = mock_tx.publish_event.call_args
            assert event_call[1]["entity_id"] == "Q42"
            assert event_call[1]["revision_id"] == 12345
            assert event_call[1]["change_type"] == ChangeType.EDIT

            # Verify user activity logging
            mock_user_repo.log_user_activity.assert_called_once()
            activity_call = mock_user_repo.log_user_activity.call_args
            assert activity_call[1]["user_id"] == 123
            assert activity_call[1]["entity_id"] == "Q42"
            assert activity_call[1]["revision_id"] == 12345

    @pytest.mark.asyncio
    async def test_update_entity_not_found(self) -> None:
        """Test entity update when entity doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = False

        handler = EntityUpdateHandler(state=mock_state)

        request = EntityUpdateRequest(
            type="item",
            data={"labels": {"en": {"value": "Updated Entity"}}}
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.update_entity("Q999", request)

        mock_vitess.entity_exists.assert_called_once_with("Q999")

    @pytest.mark.asyncio
    async def test_update_entity_deleted(self) -> None:
        """Test entity update when entity is deleted."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = True

        handler = EntityUpdateHandler(state=mock_state)

        request = EntityUpdateRequest(
            type="item",
            data={"labels": {"en": {"value": "Updated Entity"}}}
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.update_entity("Q42", request)

        mock_vitess.is_entity_deleted.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    async def test_update_entity_locked(self) -> None:
        """Test entity update when entity is locked."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = True

        handler = EntityUpdateHandler(state=mock_state)

        request = EntityUpdateRequest(
            type="item",
            data={"labels": {"en": {"value": "Updated Entity"}}}
        )

        with pytest.raises(Exception):  # Should raise validation error
            await handler.update_entity("Q42", request)

        mock_vitess.is_entity_locked.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    async def test_update_entity_transaction_failure(self) -> None:
        """Test entity update when transaction fails."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        # Mock transaction that raises exception
        mock_tx = MagicMock()
        mock_tx.get_head.side_effect = Exception("Transaction failed")

        handler = EntityUpdateHandler(state=mock_state)

        with patch("models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction") as mock_tx_class:
            mock_tx_class.return_value = mock_tx

            request = EntityUpdateRequest(
                type="item",
                data={"labels": {"en": {"value": "Updated Entity"}}}
            )

            with pytest.raises(Exception):  # Should propagate transaction exception
                await handler.update_entity("Q42", request)

    @pytest.mark.asyncio
    async def test_update_entity_user_activity_logging_failure(self) -> None:
        """Test entity update when user activity logging fails."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        mock_vitess.user_repository = mock_user_repo

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False
        mock_user_repo.log_user_activity.return_value = MagicMock(success=False, error="DB error")

        mock_tx = MagicMock()
        mock_tx.head_revision_id = 12344
        mock_tx.process_statements.return_value = MagicMock()

        mock_response = EntityResponse(
            id="Q42",
            revision_id=12345,
            entity_data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event.return_value = None

        handler = EntityUpdateHandler(state=mock_state)

        with patch("models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction") as mock_tx_class:
            mock_tx_class.return_value = mock_tx

            request = EntityUpdateRequest(
                type="item",
                data={"labels": {"en": {"value": "Updated Entity"}}}
            )

            # Should still succeed despite logging failure
            result = await handler.update_entity("Q42", request, user_id=123)

            assert result.id == "Q42"
            mock_user_repo.log_user_activity.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_entity_no_user_activity_logging(self) -> None:
        """Test entity update without user activity logging."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_tx = MagicMock()
        mock_tx.head_revision_id = 12344
        mock_tx.process_statements.return_value = MagicMock()

        mock_response = EntityResponse(
            id="Q42",
            revision_id=12345,
            entity_data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event.return_value = None

        handler = EntityUpdateHandler(state=mock_state)

        with patch("models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction") as mock_tx_class:
            mock_tx_class.return_value = mock_tx

            request = EntityUpdateRequest(
                type="item",
                data={"labels": {"en": {"value": "Updated Entity"}}}
            )

            result = await handler.update_entity("Q42", request)  # No user_id

            assert result.id == "Q42"
            # Should not attempt user activity logging
            mock_vitess.user_repository.log_user_activity.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_entity_with_validator(self) -> None:
        """Test entity update with custom validator."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_validator = MagicMock()
        mock_tx = MagicMock()
        mock_tx.head_revision_id = 12344
        mock_tx.process_statements.return_value = MagicMock()

        mock_response = EntityResponse(
            id="Q42",
            revision_id=12345,
            entity_data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event.return_value = None

        handler = EntityUpdateHandler(state=mock_state)

        with patch("models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction") as mock_tx_class:
            mock_tx_class.return_value = mock_tx

            request = EntityUpdateRequest(
                type="item",
                data={"labels": {"en": {"value": "Updated Entity"}}}
            )

            result = await handler.update_entity("Q42", request, validator=mock_validator)

            assert result.id == "Q42"
            # Verify validator was passed to process_statements
            mock_tx.process_statements.assert_called_once()
            process_call = mock_tx.process_statements.call_args
            assert process_call[0][2] == mock_validator  # Third argument is validator

    @pytest.mark.asyncio
    async def test_update_entity_mass_edit(self) -> None:
        """Test entity update with mass edit parameters."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_tx = MagicMock()
        mock_tx.head_revision_id = 12344
        mock_tx.process_statements.return_value = MagicMock()

        mock_response = EntityResponse(
            id="Q42",
            revision_id=12345,
            entity_data={"id": "Q42", "type": "item"},
            state=MagicMock()
        )
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event.return_value = None

        handler = EntityUpdateHandler(state=mock_state)

        with patch("models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction") as mock_tx_class:
            mock_tx_class.return_value = mock_tx

            request = EntityUpdateRequest(
                type="item",
                data={"labels": {"en": {"value": "Updated Entity"}}},
                is_mass_edit=True,
                edit_type="mass_edit",
                edit_summary="Bulk update",
                is_semi_protected=True,
                is_locked=False,
                is_archived=False,
                is_dangling=False,
                is_mass_edit_protected=False,
                user_id=456
            )

            result = await handler.update_entity("Q42", request)

            assert result.id == "Q42"
            # Verify mass edit parameters are passed to create_revision
            mock_tx.create_revision.assert_called_once()
            create_call = mock_tx.create_revision.call_args[1]
            assert create_call["is_mass_edit"] is True
            assert create_call["edit_type"] == "mass_edit"
            assert create_call["edit_summary"] == "Bulk update"
            assert create_call["is_semi_protected"] is True
            assert create_call["user_id"] == 456