"""Unit tests for redirects service."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException


class TestRedirectService:
    """Unit tests for RedirectService."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        state.s3_client = MagicMock()
        return state

    @pytest.fixture
    def service(self, mock_state):
        """Create service with mock state."""
        from models.rest_api.entitybase.v1.services.redirects import RedirectService

        svc = RedirectService(state=mock_state)
        return svc

    def test_validate_redirect_self(self, service, mock_state):
        """Test redirect validation fails when redirecting to self."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest

        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q1")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(mock_request)

        assert exc_info.value.status_code == 400

    def test_validate_redirect_already_exists(self, service, mock_state):
        """Test redirect validation fails when redirect already exists."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest

        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(mock_request)

        assert exc_info.value.status_code == 409

    def test_validate_source_deleted(self, service, mock_state):
        """Test redirect validation fails when source is deleted."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest

        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = True
        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(mock_request)

        assert exc_info.value.status_code == 423

    def test_validate_target_deleted(self, service, mock_state):
        """Test redirect validation fails when target is deleted."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest

        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.side_effect = [False, True]
        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(mock_request)

        assert exc_info.value.status_code == 423

    def test_validate_target_locked(self, service, mock_state):
        """Test redirect validation fails when target is locked."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest

        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True
        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(mock_request)

        assert exc_info.value.status_code == 423

    def test_validate_target_archived(self, service, mock_state):
        """Test redirect validation fails when target is archived."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest

        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_client.is_entity_archived.return_value = True
        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")

        with pytest.raises(HTTPException) as exc_info:
            service._validate_redirect_request(mock_request)

        assert exc_info.value.status_code == 423

    def test_validate_target_no_revisions(self, service, mock_state):
        """Test redirect validation fails when target has no revisions."""
        mock_state.vitess_client.get_head.return_value = 0

        with pytest.raises(HTTPException) as exc_info:
            service._validate_target_revisions("Q1", "Q2")

        assert exc_info.value.status_code == 404

    def test_validate_target_revisions_with_from_head(self, service, mock_state):
        """Test _validate_target_revisions returns correct revision IDs."""
        mock_state.vitess_client.get_head.side_effect = [10, 5]

        from_head, to_head = service._validate_target_revisions("Q1", "Q2")

        assert to_head == 10
        assert from_head == 5
        assert mock_state.vitess_client.get_head.call_count == 2

    def test_validate_target_revisions_from_head_zero(self, service, mock_state):
        """Test _validate_target_revisions when from_head is 0."""
        mock_state.vitess_client.get_head.side_effect = [10, 0]

        from_head, to_head = service._validate_target_revisions("Q1", "Q2")

        assert to_head == 10
        assert from_head == 0
        assert mock_state.vitess_client.get_head.call_count == 2

    @pytest.mark.asyncio
    async def test_create_redirect_success(self, service, mock_state):
        """Test successful redirect creation."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
        from models.data.infrastructure.s3.revision.revision_data import RevisionData

        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")
        mock_edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test redirect")

        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_client.is_entity_archived.return_value = False
        mock_state.vitess_client.get_head.side_effect = [10, 5]
        mock_state.vitess_client.create_revision.return_value = True
        mock_state.entity_change_stream_producer = None

        with patch(
            "models.rest_api.entitybase.v1.services.redirects.RevisionData"
        ) as MockRevisionData, patch(
            "models.rest_api.entitybase.v1.services.redirects.MetadataExtractor"
        ) as MockMetadataExtractor, patch(
            "models.rest_api.entitybase.v1.services.redirects.S3RevisionData"
        ) as MockS3RevisionData:
            mock_revision_instance = MagicMock()
            mock_revision_instance.model_dump.return_value = {}
            MockRevisionData.return_value = mock_revision_instance
            MockMetadataExtractor.hash_string.return_value = 12345
            MockS3RevisionData.return_value = MagicMock()

            response = await service.create_redirect(mock_request, mock_edit_headers)

            assert response.redirect_from_id == "Q1"
            assert response.redirect_to_id == "Q2"
            mock_state.vitess_client.create_revision.assert_called_once()
            mock_state.vitess_client.create_redirect.assert_called_once()
            mock_state.vitess_client.set_redirect_target.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_redirect_revision_conflict(self, service, mock_state):
        """Test redirect creation fails when revision conflict occurs."""
        from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_request = EntityRedirectRequest(redirect_from_id="Q1", redirect_to_id="Q2")
        mock_edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test redirect")

        mock_state.vitess_client.get_redirect_target.return_value = None
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_client.is_entity_archived.return_value = False
        mock_state.vitess_client.get_head.side_effect = [10, 5]
        mock_state.vitess_client.create_revision.return_value = False
        mock_state.entity_change_stream_producer = None

        with patch(
            "models.rest_api.entitybase.v1.services.redirects.RevisionData"
        ) as MockRevisionData, patch(
            "models.rest_api.entitybase.v1.services.redirects.MetadataExtractor"
        ) as MockMetadataExtractor, patch(
            "models.rest_api.entitybase.v1.services.redirects.S3RevisionData"
        ) as MockS3RevisionData:
            mock_revision_instance = MagicMock()
            mock_revision_instance.model_dump.return_value = {}
            MockRevisionData.return_value = mock_revision_instance
            MockMetadataExtractor.hash_string.return_value = 12345
            MockS3RevisionData.return_value = MagicMock()

            with pytest.raises(HTTPException) as exc_info:
                await service.create_redirect(mock_request, mock_edit_headers)

            assert exc_info.value.status_code == 409
            assert "Conflict" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_revert_redirect_success(self, service, mock_state):
        """Test successful redirect revert."""
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
        from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler

        mock_edit_headers = EditHeaders(x_user_id=123, x_edit_summary="revert redirect")
        mock_revert_response = MagicMock()

        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_client.is_entity_archived.return_value = False

        with patch.object(EntityRevertHandler, "revert_entity", return_value=mock_revert_response):
            response = await service.revert_redirect("Q1", 10, mock_edit_headers)

            assert response == mock_revert_response
            mock_state.vitess_client.revert_redirect.assert_called_once_with("Q1")

    @pytest.mark.asyncio
    async def test_revert_redirect_not_redirect(self, service, mock_state):
        """Test revert fails when entity is not a redirect."""
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_edit_headers = EditHeaders(x_user_id=123, x_edit_summary="revert redirect")

        mock_state.vitess_client.get_redirect_target.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await service.revert_redirect("Q1", 10, mock_edit_headers)

        assert exc_info.value.status_code == 404
        assert "not a redirect" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_revert_redirect_deleted(self, service, mock_state):
        """Test revert fails when entity is deleted."""
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_edit_headers = EditHeaders(x_user_id=123, x_edit_summary="revert redirect")

        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        mock_state.vitess_client.is_entity_deleted.return_value = True

        with pytest.raises(HTTPException) as exc_info:
            await service.revert_redirect("Q1", 10, mock_edit_headers)

        assert exc_info.value.status_code == 423
        assert "deleted" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_revert_redirect_locked(self, service, mock_state):
        """Test revert fails when entity is locked."""
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_edit_headers = EditHeaders(x_user_id=123, x_edit_summary="revert redirect")

        mock_state.vitess_client.get_redirect_target.return_value = "Q2"
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True

        with pytest.raises(HTTPException) as exc_info:
            await service.revert_redirect("Q1", 10, mock_edit_headers)

        assert exc_info.value.status_code == 423
        assert "locked" in str(exc_info.value.detail)
