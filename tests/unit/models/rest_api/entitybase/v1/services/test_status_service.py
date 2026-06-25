"""Unit tests for StatusService."""

import sys
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

import pytest

sys.path.insert(0, "src")

from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.data.rest_api.v1.entitybase.request.entity.entity_status import (
    EntityStatusRequest,
)
from models.rest_api.entitybase.v1.services.status_service import (
    StatusOperation,
    StatusService,
)


class TestStatusService:
    """Unit tests for StatusService."""

    def create_mock_state(self):
        """Create a mock state with vitess and s3 clients."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        return mock_state

    def create_mock_revision(self, state: EntityState | None = None):
        """Create a mock S3 revision."""
        if state is None:
            state = EntityState(
                is_semi_protected=False,
                is_locked=False,
                is_archived=False,
                is_dangling=False,
                is_mass_edit_protected=False,
                is_deleted=False,
            )
        return S3RevisionData(
            schema="3.0.0",
            revision={
                "entity_type": "item",
                "labels_hashes": {},
                "descriptions_hashes": {},
                "aliases_hashes": {},
                "statements": [],
                "sitelinks": {},
                "properties": [],
                "state": {
                    "sp": state.is_semi_protected,
                    "locked": state.is_locked,
                    "archived": state.is_archived,
                    "dangling": state.is_dangling,
                    "mep": state.is_mass_edit_protected,
                    "deleted": state.is_deleted,
                },
            },
            hash=123456789,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def test_validate_preconditions_success(self):
        """Test validate_preconditions passes when clients are initialized."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        service.validate_preconditions()

    def test_validate_preconditions_vitess_none(self):
        """Test validate_preconditions raises when vitess is None."""
        mock_state = MagicMock()
        mock_state.vitess_client = None
        mock_state.s3_client = MagicMock()

        service = StatusService(state=mock_state)

        with pytest.raises(Exception) as exc_info:
            service.validate_preconditions()
        assert "Vitess not initialized" in str(exc_info.value)

    def test_validate_preconditions_s3_none(self):
        """Test validate_preconditions raises when s3 is None."""
        mock_state = MagicMock()
        mock_state.vitess_client = MagicMock()
        mock_state.s3_client = None

        service = StatusService(state=mock_state)

        with pytest.raises(Exception) as exc_info:
            service.validate_preconditions()
        assert "S3 not initialized" in str(exc_info.value)

    def test_validate_entity_exists_not_found(self):
        """Test validate_entity_exists raises 404 when entity doesn't exist."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = False

        service = StatusService(state=mock_state)

        with pytest.raises(Exception) as exc_info:
            service.validate_entity_exists("Q99999")
        assert "Entity not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    def test_validate_entity_exists_deleted(self):
        """Test validate_entity_exists raises 410 when entity is deleted."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = True

        service = StatusService(state=mock_state)

        with pytest.raises(Exception) as exc_info:
            service.validate_entity_exists("Q99999")
        assert "has been deleted" in str(exc_info.value)
        assert exc_info.value.status_code == 410

    def test_validate_entity_exists_success(self):
        """Test validate_entity_exists returns head revision ID."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42

        service = StatusService(state=mock_state)

        result = service.validate_entity_exists("Q42")

        assert result == 42

    def test_validate_entity_exists_no_revisions(self):
        """Test validate_entity_exists raises 404 when no revisions."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 0

        service = StatusService(state=mock_state)

        with pytest.raises(Exception) as exc_info:
            service.validate_entity_exists("Q42")
        assert "Entity not found" in str(exc_info.value)

    def test_change_status_entity_not_found(self):
        """Test change_status raises 404 when entity doesn't exist."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = False

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        with pytest.raises(Exception) as exc_info:
            service.change_status("Q99999", StatusOperation.LOCK, request)
        assert exc_info.value.status_code == 404

    def test_change_status_entity_deleted(self):
        """Test change_status raises 410 when entity is deleted."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = True

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        with pytest.raises(Exception) as exc_info:
            service.change_status("Q99999", StatusOperation.LOCK, request)
        assert exc_info.value.status_code == 410

    def test_change_status_idempotent_lock(self):
        """Test change_status returns idempotent response when already locked."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42

        current_state = EntityState(
            sp=False,
            locked=True,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.LOCK, request)

        assert result.id == "Q42"
        assert result.revision_id == 42
        assert result.status == "locked"
        assert result.idempotent is True

    def test_change_status_idempotent_unlock(self):
        """Test change_status returns idempotent response when already unlocked."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.UNLOCK, request)

        assert result.id == "Q42"
        assert result.revision_id == 42
        assert result.status == "unlocked"
        assert result.idempotent is True

    def test_change_status_idempotent_archive(self):
        """Test change_status returns idempotent response when already archived."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=True,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.ARCHIVE, request)

        assert result.id == "Q42"
        assert result.revision_id == 42
        assert result.status == "archived"
        assert result.idempotent is True

    def test_change_status_idempotent_semi_protect(self):
        """Test change_status returns idempotent response when already semi-protected."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42

        current_state = EntityState(
            sp=True,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.SEMI_PROTECT, request)

        assert result.id == "Q42"
        assert result.revision_id == 42
        assert result.status == "semi_protected"
        assert result.idempotent is True

    def test_change_status_idempotent_mass_edit_protect(self):
        """Test change_status returns idempotent response when already mass-edit protected."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=True,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status(
            "Q42", StatusOperation.MASS_EDIT_PROTECT, request
        )

        assert result.id == "Q42"
        assert result.revision_id == 42
        assert result.status == "mass_edit_protected"
        assert result.idempotent is True

    def test_get_status_string_lock(self):
        """Test _get_status_string returns correct value for LOCK."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._get_status_string(StatusOperation.LOCK)

        assert result == "locked"

    def test_get_status_string_unlock(self):
        """Test _get_status_string returns correct value for UNLOCK."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._get_status_string(StatusOperation.UNLOCK)

        assert result == "unlocked"

    def test_get_status_string_archive(self):
        """Test _get_status_string returns correct value for ARCHIVE."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._get_status_string(StatusOperation.ARCHIVE)

        assert result == "archived"

    def test_get_status_string_unarchive(self):
        """Test _get_status_string returns correct value for UNARCHIVE."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._get_status_string(StatusOperation.UNARCHIVE)

        assert result == "unarchived"

    def test_get_status_string_semi_protect(self):
        """Test _get_status_string returns correct value for SEMI_PROTECT."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._get_status_string(StatusOperation.SEMI_PROTECT)

        assert result == "semi_protected"

    def test_get_status_string_mass_edit_protect(self):
        """Test _get_status_string returns correct value for MASS_EDIT_PROTECT."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._get_status_string(StatusOperation.MASS_EDIT_PROTECT)

        assert result == "mass_edit_protected"

    def test_change_status_success(self):
        """Test change_status successfully changes status (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest(edit_summary="locking entity")

        result = service.change_status("Q42", StatusOperation.LOCK, request)

        assert result.id == "Q42"
        assert result.revision_id == 43
        assert result.status == "locked"
        assert result.idempotent is False
        mock_state.vitess_client.create_revision.assert_called_once()

    def test_change_status_s3_read_failure(self):
        """Test change_status raises 404 when S3 read fails."""
        from fastapi import HTTPException

        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.s3_client.read_revision.side_effect = Exception("S3 error")

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        with pytest.raises(HTTPException) as exc_info:
            service.change_status("Q42", StatusOperation.LOCK, request)
        assert exc_info.value.status_code == 404

    def test_change_status_state_none(self):
        """Test change_status handles revision state being None."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        revision_data = self.create_mock_revision()
        revision_data.revision["state"] = None
        mock_state.s3_client.read_revision.return_value = revision_data
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.LOCK, request)

        assert result.id == "Q42"
        assert result.status == "locked"
        assert result.idempotent is False

    def test_change_status_non_idempotent_unlock(self):
        """Test change_status unlocked (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=True,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.UNLOCK, request)

        assert result.id == "Q42"
        assert result.status == "unlocked"
        assert result.idempotent is False

    def test_change_status_non_idempotent_archive(self):
        """Test change_status archived (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.ARCHIVE, request)

        assert result.id == "Q42"
        assert result.status == "archived"
        assert result.idempotent is False

    def test_change_status_non_idempotent_unarchive(self):
        """Test change_status unarchived (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=True,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.UNARCHIVE, request)

        assert result.id == "Q42"
        assert result.status == "unarchived"
        assert result.idempotent is False

    def test_change_status_non_idempotent_semi_protect(self):
        """Test change_status semi_protected (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.SEMI_PROTECT, request)

        assert result.id == "Q42"
        assert result.status == "semi_protected"
        assert result.idempotent is False

    def test_change_status_non_idempotent_unsemi_protect(self):
        """Test change_status unsemi_protected (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=True,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status("Q42", StatusOperation.UNSEMI_PROTECT, request)

        assert result.id == "Q42"
        assert result.status == "unprotected"
        assert result.idempotent is False

    def test_change_status_non_idempotent_mass_edit_protect(self):
        """Test change_status mass_edit_protected (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status(
            "Q42", StatusOperation.MASS_EDIT_PROTECT, request
        )

        assert result.id == "Q42"
        assert result.status == "mass_edit_protected"
        assert result.idempotent is False

    def test_change_status_non_idempotent_mass_edit_unprotect(self):
        """Test change_status mass_edit_unprotected (non-idempotent)."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.return_value = 42
        mock_state.vitess_client.create_revision.return_value = True

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=True,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        result = service.change_status(
            "Q42", StatusOperation.MASS_EDIT_UNPROTECT, request
        )

        assert result.id == "Q42"
        assert result.status == "mass_edit_unprotected"
        assert result.idempotent is False

    def test_change_status_conflict(self):
        """Test change_status raises 409 on conflict."""
        from fastapi import HTTPException

        mock_state = self.create_mock_state()
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.get_head.side_effect = [42, 50]
        mock_state.vitess_client.create_revision.return_value = False

        current_state = EntityState(
            sp=False,
            locked=False,
            archived=False,
            dangling=False,
            mep=False,
            deleted=False,
        )
        mock_revision = self.create_mock_revision(current_state)
        mock_state.s3_client.read_revision.return_value = mock_revision
        mock_state.s3_client.store_revision.return_value = (999, MagicMock())

        service = StatusService(state=mock_state)
        request = EntityStatusRequest()

        with pytest.raises(HTTPException) as exc_info:
            service.change_status("Q42", StatusOperation.LOCK, request)
        assert exc_info.value.status_code == 409
        assert "Conflict" in exc_info.value.detail

    def test_check_is_in_target_state_true(self):
        """Test _check_is_in_target_state returns True when in target state."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._check_is_in_target_state(
            StatusOperation.LOCK, {"locked": True}
        )

        assert result is True

    def test_check_is_in_target_state_false(self):
        """Test _check_is_in_target_state returns False when not in target state."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._check_is_in_target_state(
            StatusOperation.LOCK, {"locked": False}
        )

        assert result is False

    def test_check_is_in_target_state_empty(self):
        """Test _check_is_in_target_state returns False for empty state."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        result = service._check_is_in_target_state(StatusOperation.LOCK, {})

        assert result is False

    def test_get_target_state_key_value(self):
        """Test _get_target_state_key_value returns correct tuple."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        key, value = service._get_target_state_key_value(StatusOperation.LOCK)
        assert key == "locked"
        assert value is True

        key, value = service._get_target_state_key_value(StatusOperation.ARCHIVE)
        assert key == "archived"
        assert value is True

        key, value = service._get_target_state_key_value(StatusOperation.SEMI_PROTECT)
        assert key == "sp"
        assert value is True

    def test_get_edit_type(self):
        """Test _get_edit_type returns correct EditType."""
        mock_state = self.create_mock_state()
        service = StatusService(state=mock_state)

        from models.data.infrastructure.s3.enums import EditType

        assert service._get_edit_type(StatusOperation.LOCK) == EditType.LOCK_ADDED
        assert service._get_edit_type(StatusOperation.UNLOCK) == EditType.LOCK_REMOVED
        assert service._get_edit_type(StatusOperation.ARCHIVE) == EditType.ARCHIVE_ADDED
        assert (
            service._get_edit_type(StatusOperation.UNARCHIVE)
            == EditType.ARCHIVE_REMOVED
        )
        assert (
            service._get_edit_type(StatusOperation.SEMI_PROTECT)
            == EditType.SEMI_PROTECT_ADDED
        )
        assert (
            service._get_edit_type(StatusOperation.MASS_EDIT_PROTECT)
            == EditType.MASS_EDIT_PROTECT_ADDED
        )
