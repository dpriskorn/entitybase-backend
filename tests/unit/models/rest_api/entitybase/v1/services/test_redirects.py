"""Unit tests for redirects service."""

import pytest
from unittest.mock import MagicMock
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
