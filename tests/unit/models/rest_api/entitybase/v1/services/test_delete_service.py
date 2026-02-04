"""Unit tests for DeleteService."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.rest_api.entitybase.v1.services.delete_service import DeleteService
from models.data.rest_api.v1.entitybase.request import EntityDeleteRequest
from models.data.infrastructure.s3.enums import DeleteType


class TestDeleteService:
    """Unit tests for DeleteService."""

    # validate_delete_preconditions
    def test_validate_delete_preconditions_success(self) -> None:
        """Test validating delete preconditions with both clients initialized."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        service = DeleteService(state=mock_state)
        service.validate_delete_preconditions()

        assert True  # No exception raised

    def test_validate_delete_preconditions_vitess_none(self) -> None:
        """Test validating delete preconditions when Vitess is None."""
        mock_state = MagicMock()
        mock_state.vitess_client = None

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_delete_preconditions()

    def test_validate_delete_preconditions_s3_none(self) -> None:
        """Test validating delete preconditions when S3 is None."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = None

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_delete_preconditions()

    # validate_entity_state
    def test_validate_entity_state_success(self) -> None:
        """Test validating entity state with valid entity."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.get_head.return_value = 3

        service = DeleteService(state=mock_state)
        head_rev = service.validate_entity_state("Q42")

        assert head_rev == 3

    def test_validate_entity_state_not_found(self) -> None:
        """Test validating entity state when entity doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = False

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_entity_state("Q999")

    def test_validate_entity_state_already_deleted(self) -> None:
        """Test validating entity state when entity is already deleted."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = True

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_entity_state("Q42")

    def test_validate_entity_state_no_head_revision(self) -> None:
        """Test validating entity state when there's no head revision."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.get_head.return_value = 0

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_entity_state("Q42")

    # validate_protection_status
    def test_validate_protection_status_success(self) -> None:
        """Test validating protection status when entity is not protected."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.get_protection_info.return_value = None

        service = DeleteService(state=mock_state)
        service.validate_protection_status("Q42")

        assert True  # No exception raised

    def test_validate_protection_status_archived(self) -> None:
        """Test validating protection status when entity is archived."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_protection = MagicMock()
        mock_protection.is_archived = True
        mock_vitess.get_protection_info.return_value = mock_protection

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_protection_status("Q42")

    def test_validate_protection_status_locked(self) -> None:
        """Test validating protection status when entity is locked."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_protection = MagicMock()
        mock_protection.get.return_value = True  # is_locked
        mock_vitess.get_protection_info.return_value = mock_protection

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.validate_protection_status("Q42")

    # build_deletion_revision (static)
    def test_build_deletion_revision_soft_delete(self) -> None:
        """Test building deletion revision for soft delete."""
        mock_current = MagicMock()
        mock_current.revision = {
            "entity_type": "item",
            "properties": {},
            "property_counts": {},
            "statements": [],
            "sitelinks": {},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
        }

        request = EntityDeleteRequest(
            delete_type=DeleteType.SOFT,
            deletion_reason="Test deletion",
            deleted_by="test_user",
        )

        revision_data = DeleteService.build_deletion_revision(
            "Q42",
            mock_current,
            3,
            request,
            123,
            "Delete entity",
        )

        assert revision_data.revision_id == 3
        assert revision_data.entity_type.value == "item"
        assert revision_data.state.deleted is True
        from models.data.infrastructure.s3.enums import EditType
        assert revision_data.edit.type == EditType.SOFT_DELETE

    def test_build_deletion_revision_hard_delete(self) -> None:
        """Test building deletion revision for hard delete."""
        mock_current = MagicMock()
        mock_current.revision = {"entity_type": "item"}

        request = EntityDeleteRequest(
            delete_type=DeleteType.HARD,
            deletion_reason="Test deletion",
            deleted_by="test_user",
        )

        revision_data = DeleteService.build_deletion_revision(
            "Q42",
            mock_current,
            3,
            request,
            123,
            "Delete entity",
        )

        from models.data.infrastructure.s3.enums import EditType
        assert revision_data.edit.type == EditType.HARD_DELETE

    def test_build_deletion_revision_preserves_state(self) -> None:
        """Test building deletion revision preserves current state flags."""
        mock_current = MagicMock()
        mock_current.revision = {
            "is_semi_protected": True,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False,
        }

        request = EntityDeleteRequest(
            delete_type=DeleteType.SOFT,
            deletion_reason="Test",
            deleted_by="test_user",
        )

        revision_data = DeleteService.build_deletion_revision(
            "Q42",
            mock_current,
            3,
            request,
            123,
            "Delete",
        )

        assert revision_data.state.sp is True
        assert revision_data.state.locked is False
        assert revision_data.state.archived is False

    def test_build_deletion_revision_sets_deleted_flag(self) -> None:
        """Test building deletion revision sets deleted=True."""
        mock_current = MagicMock()
        mock_current.revision = {"entity_type": "item"}

        request = EntityDeleteRequest(
            delete_type=DeleteType.SOFT,
            deletion_reason="Test",
            deleted_by="test_user",
        )

        revision_data = DeleteService.build_deletion_revision(
            "Q42",
            mock_current,
            3,
            request,
            123,
            "Delete",
        )

        assert revision_data.state.deleted is True

    # decrement_statement_references
    def test_decrement_statement_references_success(self) -> None:
        """Test decrementing statement references."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.decrement_ref_count = MagicMock()

        service = DeleteService(state=mock_state)
        service.decrement_statement_references([12345, 67890])

        assert mock_vitess.decrement_ref_count.call_count == 2

    def test_decrement_statement_references_handles_failure(self) -> None:
        """Test decrementing statement references handles failures gracefully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.decrement_ref_count.side_effect = Exception("DB error")

        service = DeleteService(state=mock_state)
        service.decrement_statement_references([12345])

        assert True  # No exception raised, just logged

    # store_deletion_revision
    def test_store_deletion_revision_success(self) -> None:
        """Test storing deletion revision to S3."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.store_revision = MagicMock()

        mock_revision_data = MagicMock()
        mock_revision_data.revision_id = 3
        mock_revision_data.model_dump = MagicMock(return_value={})

        service = DeleteService(state=mock_state)
        content_hash, s3_data = service.store_deletion_revision(mock_revision_data)

        assert content_hash is not None
        assert s3_data is not None
        mock_s3.store_revision.assert_called_once()

    def test_store_deletion_revision_s3_failure(self) -> None:
        """Test storing deletion revision when S3 fails."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.store_revision.side_effect = Exception("S3 error")

        mock_revision_data = MagicMock()
        mock_revision_data.model_dump = MagicMock(return_value={})

        service = DeleteService(state=mock_state)

        with pytest.raises(ValueError):
            service.store_deletion_revision(mock_revision_data)

    # publish_delete_event
    @pytest.mark.asyncio
    async def test_publish_delete_event_success(self) -> None:
        """Test publishing delete event successfully."""
        mock_state = MagicMock()
        mock_producer = MagicMock()
        mock_producer.publish_change = AsyncMock()
        mock_state.entity_change_stream_producer = mock_producer

        service = DeleteService(state=mock_state)
        await service.publish_delete_event("Q42", 3, 2, "Delete entity")

        mock_producer.publish_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_delete_event_no_producer(self) -> None:
        """Test publishing delete event when producer is not available."""
        mock_state = MagicMock()
        mock_state.entity_change_stream_producer = None

        service = DeleteService(state=mock_state)
        await service.publish_delete_event("Q42", 3, 2, "Delete entity")

        assert True  # No exception raised

    @pytest.mark.asyncio
    async def test_publish_delete_event_publish_failure(self) -> None:
        """Test publishing delete event handles publish failure."""
        mock_state = MagicMock()
        mock_producer = MagicMock()
        mock_producer.publish_change = AsyncMock(side_effect=Exception("Kafka error"))
        mock_state.entity_change_stream_producer = mock_producer

        service = DeleteService(state=mock_state)
        await service.publish_delete_event("Q42", 3, 2, "Delete entity")

        assert True  # No exception raised, just logged

    # log_delete_activity
    def test_log_delete_activity_success(self) -> None:
        """Test logging delete activity successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.user_repository = mock_user_repo
        mock_user_repo.log_user_activity.return_value = MagicMock(success=True)

        service = DeleteService(state=mock_state)
        service.log_delete_activity(123, "Q42", 3)

        mock_user_repo.log_user_activity.assert_called_once()

    def test_log_delete_activity_no_user_id(self) -> None:
        """Test logging delete activity with user_id=0."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.user_repository = mock_user_repo

        service = DeleteService(state=mock_state)
        service.log_delete_activity(0, "Q42", 3)

        # Should not call log_user_activity when user_id is 0
        mock_user_repo.log_user_activity.assert_not_called()

    def test_log_delete_activity_failure(self) -> None:
        """Test logging delete activity handles failure."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.user_repository = mock_user_repo
        mock_user_repo.log_user_activity.return_value = MagicMock(success=False, error="DB error")

        service = DeleteService(state=mock_state)
        service.log_delete_activity(123, "Q42", 3)

        assert True  # No exception raised
