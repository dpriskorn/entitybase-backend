"""Unit tests for redirects service."""

from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.rest_api.entitybase.v1.services.redirects import RedirectService


class TestRedirectService:
    """Unit tests for RedirectService."""

    def create_mock_state(self):
        """Create a mock state with vitess and s3 clients."""
        mock_state = MagicMock()
        mock_state.vitess_client = MagicMock()
        mock_state.s3_client = MagicMock()
        mock_state.entity_change_stream_producer = None
        return mock_state

    def test_validate_redirect_request_self_redirect(self):
        """Test _validate_redirect_request raises when redirecting to self."""
        mock_state = self.create_mock_state()
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q1",
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(request)
        assert exc_info.value.status_code == 400
        assert "Cannot redirect to self" in exc_info.value.detail

    def test_validate_redirect_request_already_exists(self):
        """Test _validate_redirect_request raises when redirect already exists."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(request)
        assert exc_info.value.status_code == 409
        assert "Redirect already exists" in exc_info.value.detail

    def test_validate_redirect_request_source_deleted(self):
        """Test _validate_redirect_request raises when source entity is deleted."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.side_effect = lambda e: e == "Q1"
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(request)
        assert exc_info.value.status_code == 423
        assert "Source entity has been deleted" in exc_info.value.detail

    def test_validate_redirect_request_target_deleted(self):
        """Test _validate_redirect_request raises when target entity is deleted."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.side_effect = lambda e: e == "Q2"
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(request)
        assert exc_info.value.status_code == 423
        assert "Target entity has been deleted" in exc_info.value.detail

    def test_validate_redirect_request_target_locked(self):
        """Test _validate_redirect_request raises when target is locked."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(request)
        assert exc_info.value.status_code == 423
        assert "Target entity is locked or archived" in exc_info.value.detail

    def test_validate_redirect_request_target_archived(self):
        """Test _validate_redirect_request raises when target is archived."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_client.is_entity_archived.return_value = True
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(request)
        assert exc_info.value.status_code == 423
        assert "Target entity is locked or archived" in exc_info.value.detail

    def test_validate_redirect_request_success(self):
        """Test _validate_redirect_request passes for valid request."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_client.is_entity_archived.return_value = False
        service = RedirectService(state=mock_state)

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )

        service._validate_redirect_request(request)

    def test_validate_target_revisions_no_revisions(self):
        """Test _validate_target_revisions raises when target has no revisions."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_head.return_value = 0
        service = RedirectService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            service._validate_target_revisions("Q1", "Q2")
        assert exc_info.value.status_code == 404
        assert "Target entity has no revisions" in exc_info.value.detail

    def test_validate_target_revisions_success(self):
        """Test _validate_target_revisions returns head revisions."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_head.side_effect = [10, 20]
        service = RedirectService(state=mock_state)

        from_rev, to_rev = service._validate_target_revisions("Q1", "Q2")

        assert from_rev == 20
        assert to_rev == 10

    def test_validate_target_revisions_no_source_revisions(self):
        """Test _validate_target_revisions handles source with no revisions."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_head.side_effect = [10, 0]
        service = RedirectService(state=mock_state)

        from_rev, to_rev = service._validate_target_revisions("Q1", "Q2")

        assert from_rev == 0
        assert to_rev == 10

    def test_create_redirect_revision_success(self):
        """Test _create_redirect_revision creates revision data."""
        mock_state = self.create_mock_state()
        mock_state.s3_client.store_revision = MagicMock()
        service = RedirectService(state=mock_state)

        edit_headers = EditHeaders(x_user_id=1, x_edit_summary="Creating redirect")

        revision_data, content_hash = service._create_redirect_revision(
            "Q1", "Q2", edit_headers, from_head_revision_id=10
        )

        assert revision_data.revision_id == 11
        assert revision_data.redirects_to == "Q2"
        assert content_hash > 0

    @pytest.mark.asyncio
    async def test_revert_redirect_not_redirect(self):
        """Test revert_redirect raises when entity is not a redirect."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = None
        service = RedirectService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            await service.revert_redirect("Q1", 10, EditHeaders(x_user_id=0, x_edit_summary="test"))
        assert exc_info.value.status_code == 404
        assert "not a redirect" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_revert_redirect_source_deleted(self):
        """Test revert_redirect raises when source entity is deleted."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        mock_state.vitess_client.is_entity_deleted.return_value = True
        service = RedirectService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            await service.revert_redirect("Q1", 10, EditHeaders(x_user_id=0, x_edit_summary="test"))
        assert exc_info.value.status_code == 423
        assert "deleted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_revert_redirect_entity_locked(self):
        """Test revert_redirect raises when entity is locked."""
        mock_state = self.create_mock_state()
        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True
        service = RedirectService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            await service.revert_redirect("Q1", 10, EditHeaders(x_user_id=0, x_edit_summary="test"))
        assert exc_info.value.status_code == 423
        assert "locked or archived" in exc_info.value.detail
