"""Unit tests for EntityStatusHandler in status.py."""

from unittest.mock import MagicMock, patch
import pytest

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request.entity.entity_status import (
    EntityStatusRequest,
)
from models.data.rest_api.v1.entitybase.response.entity.entity_status import (
    EntityStatusResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.status import EntityStatusHandler


class TestEntityStatusHandler:
    """Tests for EntityStatusHandler methods."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.mysql_client.user_repository.log_user_activity.return_value = MagicMock(
            success=True
        )
        return state

    @pytest.fixture
    def handler(self, mock_state: MagicMock) -> EntityStatusHandler:
        return EntityStatusHandler(state=mock_state)

    def _make_edit_headers(self) -> EditHeaders:
        return EditHeaders(x_edit_summary="test")

    def _make_status_response(self, status: str = "locked") -> EntityStatusResponse:
        return EntityStatusResponse(
            id="Q42",
            revision_id=5,
            status=status,
        )

    def test_lock(self, handler: EntityStatusHandler, mock_state: MagicMock) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "locked"
            )

            request = EntityStatusRequest(edit_summary="locking")
            result = handler.lock("Q42", request, self._make_edit_headers(), user_id=123)

            assert result.id == "Q42"
            assert result.status == "locked"
            mock_service.change_status.assert_called_once()

    def test_unlock(self, handler: EntityStatusHandler, mock_state: MagicMock) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "unlocked"
            )

            request = EntityStatusRequest(edit_summary="unlocking")
            result = handler.unlock("Q42", request, self._make_edit_headers(), user_id=123)

            assert result.status == "unlocked"
            mock_service.change_status.assert_called_once()

    def test_archive(self, handler: EntityStatusHandler, mock_state: MagicMock) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "archived"
            )

            request = EntityStatusRequest(edit_summary="locking")
            result = handler.archive("Q42", request, self._make_edit_headers(), user_id=123)

            assert result.status == "archived"
            mock_service.change_status.assert_called_once()

    def test_unarchive(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "unarchived"
            )

            request = EntityStatusRequest(edit_summary="unlocking")
            result = handler.unarchive("Q42", request, self._make_edit_headers(), user_id=123)

            assert result.status == "unarchived"
            mock_service.change_status.assert_called_once()

    def test_semi_protect(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "semi_protected"
            )

            request = EntityStatusRequest(edit_summary="locking")
            result = handler.semi_protect("Q42", request)

            assert result.status == "semi_protected"
            mock_service.change_status.assert_called_once()

    def test_unsemi_protect(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "unprotected"
            )

            request = EntityStatusRequest(edit_summary="unlocking")
            result = handler.unsemi_protect("Q42", request)

            assert result.status == "unprotected"
            mock_service.change_status.assert_called_once()

    def test_mass_edit_protect(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "mass_edit_protected"
            )

            request = EntityStatusRequest(edit_summary="locking")
            result = handler.mass_edit_protect("Q42", request)

            assert result.id == "Q42"
            mock_service.change_status.assert_called_once()

    def test_mass_edit_unprotect(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.status.StatusService"
        ) as MockStatusService:
            mock_service = MockStatusService.return_value
            mock_service.change_status.return_value = self._make_status_response(
                "unprotected"
            )

            request = EntityStatusRequest(edit_summary="unlocking")
            result = handler.mass_edit_unprotect("Q42", request)

            assert result.id == "Q42"
            mock_service.change_status.assert_called_once()

    def test_log_activity_user_not_logged(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        from models.data.rest_api.v1.entitybase.request import UserActivityType

        handler._log_activity(0, UserActivityType.ENTITY_LOCK, "Q42")
        mock_state.mysql_client.user_repository.log_user_activity.assert_not_called()

    def test_log_activity_failure_logs_warning(
        self, handler: EntityStatusHandler, mock_state: MagicMock
    ) -> None:
        from models.data.rest_api.v1.entitybase.request import UserActivityType

        mock_state.mysql_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=False, error="DB error")
        )
        handler._log_activity(123, UserActivityType.ENTITY_LOCK, "Q42")
