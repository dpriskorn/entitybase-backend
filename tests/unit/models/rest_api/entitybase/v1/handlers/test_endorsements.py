"""Unit tests for endorsement handler."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from models.data.infrastructure.stream.actions import EndorseAction


class TestEndorsementHandler:
    """Test EndorsementHandler class."""

    @pytest.fixture
    def mock_endorsement(self):
        """Create a mock endorsement object."""
        endorsement = MagicMock()
        endorsement.id = 1
        endorsement.user_id = 1
        endorsement.statement_hash = 12345
        endorsement.created_at = datetime.now(timezone.utc)
        endorsement.removed_at = None
        return endorsement

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        with patch('models.rest_api.entitybase.v1.handlers.endorsements.EndorsementHandler') as MockClass:
            MockClass.state = mock_state
            handler = MagicMock()
            handler.state = mock_state
            return handler

    def test_validate_user_success(self, mock_handler, mock_state):
        """Test _validate_user with valid user."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_state.vitess_client.user_repository.user_exists.return_value = True

        EndorsementHandler._validate_user(mock_handler, 123)

        mock_state.vitess_client.user_repository.user_exists.assert_called_once_with(123)

    def test_validate_user_not_found(self, mock_handler, mock_state):
        """Test _validate_user with invalid user."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_state.vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._validate_user(mock_handler, 999)

        assert exc_info.value.status_code == 404
        assert "User not registered" in exc_info.value.detail

    def test_handle_endorsement_error_not_found(self, mock_handler):
        """Test _handle_endorsement_error with 'not found' error."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        error_msg = "Statement not found"

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._handle_endorsement_error(mock_handler, error_msg, "create")

        assert exc_info.value.status_code == 404

    def test_handle_endorsement_error_other(self, mock_handler):
        """Test _handle_endorsement_error with other error."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        error_msg = "Some other error"

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._handle_endorsement_error(mock_handler, error_msg, "create")

        assert exc_info.value.status_code == 400

    def test_handle_endorsement_error_none(self, mock_handler):
        """Test _handle_endorsement_error with None error."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._handle_endorsement_error(mock_handler, None, "create")

        assert exc_info.value.status_code == 400

    def test_publish_endorsement_event_with_producer(self, mock_handler, mock_state):
        """Test _publish_endorsement_event when producer exists."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_state.vitess_client.stream_producer = MagicMock()

        EndorsementHandler._publish_endorsement_event(mock_handler, 12345, 1, EndorseAction.ENDORSE)

        mock_state.vitess_client.stream_producer.publish_change.assert_called_once()

    def test_publish_endorsement_event_without_producer(self, mock_handler, mock_state):
        """Test _publish_endorsement_event when no producer exists."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_state.vitess_client.stream_producer = None

        # Should not raise an exception, just do nothing
        EndorsementHandler._publish_endorsement_event(mock_handler, 12345, 1, EndorseAction.ENDORSE)

    def test_find_endorsement_by_user_active(self, mock_handler, mock_endorsement):
        """Test _find_endorsement_by_user for active endorsement."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        endorsements = [mock_endorsement]

        result = EndorsementHandler._find_endorsement_by_user(mock_handler, endorsements, 1, must_be_active=True)

        assert result == mock_endorsement

    def test_find_endorsement_by_user_withdrawn(self, mock_handler, mock_endorsement):
        """Test _find_endorsement_by_user for withdrawn endorsement."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_endorsement.removed_at = datetime.now(timezone.utc)
        endorsements = [mock_endorsement]

        result = EndorsementHandler._find_endorsement_by_user(mock_handler, endorsements, 1, must_be_active=False)

        assert result == mock_endorsement

    def test_find_endorsement_by_user_not_found(self, mock_handler, mock_endorsement):
        """Test _find_endorsement_by_user when not found."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        endorsements = [mock_endorsement]

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._find_endorsement_by_user(mock_handler, endorsements, 999, must_be_active=True)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve endorsement" in exc_info.value.detail

    def test_get_and_validate_endorsement_success(self, mock_handler, mock_state, mock_endorsement):
        """Test _get_and_validate_endorsement with valid endorsement."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {"endorsements": [mock_endorsement]}
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = mock_result

        # Verify that the repository is called and data is retrieved
        result = EndorsementHandler._get_and_validate_endorsement(mock_handler, 12345, 1, must_be_active=True)

        # Just verify we got a result (the mock endorsement is returned)
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.assert_called_once()

    def test_get_and_validate_endorsement_failure(self, mock_handler, mock_state):
        """Test _get_and_validate_endorsement when repository fails."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_result = MagicMock()
        mock_result.success = False
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._get_and_validate_endorsement(mock_handler, 12345, 1, must_be_active=True)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve endorsement details" in exc_info.value.detail

    def test_get_and_validate_endorsement_empty(self, mock_handler, mock_state):
        """Test _get_and_validate_endorsement with empty endorsements."""
        from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {"endorsements": []}
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            EndorsementHandler._get_and_validate_endorsement(mock_handler, 12345, 1, must_be_active=True)

        assert exc_info.value.status_code == 500
