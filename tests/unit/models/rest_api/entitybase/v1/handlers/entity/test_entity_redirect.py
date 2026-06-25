"""Unit tests for redirect.py."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from models.data.rest_api.v1.entitybase.request import (
    EntityRedirectRequest,
    RedirectRevertRequest,
)
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.rest_api.entitybase.v1.handlers.entity.redirect import RedirectHandler


class TestRedirectHandler:
    """Tests for RedirectHandler methods."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.redirect_service.create_redirect = AsyncMock(return_value=MagicMock())
        state.redirect_service.revert_redirect = AsyncMock(return_value=MagicMock())
        return state

    @pytest.fixture
    def handler(self, mock_state: MagicMock) -> RedirectHandler:
        return RedirectHandler(state=mock_state)

    @pytest.mark.asyncio
    async def test_create_entity_redirect(
        self, handler: RedirectHandler, mock_state: MagicMock
    ) -> None:
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
        )
        headers = EditHeaders(x_user_id=0, x_edit_summary="create redirect")

        mock_state.redirect_service.create_redirect.return_value = MagicMock()

        result = await handler.create_entity_redirect(request, headers)

        mock_state.redirect_service.create_redirect.assert_called_once_with(
            request, headers
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_revert_entity_redirect(
        self, handler: RedirectHandler, mock_state: MagicMock
    ) -> None:
        request = RedirectRevertRequest(revert_to_revision_id=5)
        headers = EditHeaders(x_user_id=0, x_edit_summary="revert redirect")

        mock_state.redirect_service.revert_redirect.return_value = MagicMock()

        result = await handler.revert_entity_redirect("Q1", request, headers)

        mock_state.redirect_service.revert_redirect.assert_called_once_with(
            "Q1", 5, headers
        )
        assert result is not None
