"""Unit tests for LexemeCreateHandler in lexeme/create.py."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import LexemeCreateHandler


class TestLexemeCreateHandler:
    """Tests for LexemeCreateHandler."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.vitess_client.entity_exists.return_value = False
        state.vitess_client.register_entity.return_value = True
        state.vitess_client.is_entity_deleted.return_value = False
        state.vitess_client.user_repository.log_user_activity.return_value = MagicMock(success=True)
        state.s3_client = MagicMock()
        return state

    def _make_handler(self, mock_state: MagicMock) -> LexemeCreateHandler:
        handler = LexemeCreateHandler.model_construct(
            state=mock_state,
            enumeration_service=MagicMock()
        )
        return handler

    def _make_request(
        self,
        language: str = "Q1",
        lexical_category: str = "Q2",
        lemmas: dict | None = None,
    ) -> EntityCreateRequest:
        if lemmas is None:
            lemmas = {"en": {"value": "test"}}
        return EntityCreateRequest(
            type="lexeme",
            language=language,
            lexical_category=lexical_category,
            lemmas=lemmas,
        )

    @pytest.mark.asyncio
    async def test_create_lexeme_no_lemmas_raises_error(self, mock_state: MagicMock) -> None:
        handler = self._make_handler(mock_state)
        request = self._make_request(lemmas={})

        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await handler.create_entity(request, edit_headers)
        assert exc_info.value.status_code == 400
        assert "at least one lemma" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_lexeme_invalid_language_raises_error(self, mock_state: MagicMock) -> None:
        handler = self._make_handler(mock_state)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await handler.create_entity(
                self._make_request(language="invalid"),
                EditHeaders(x_user_id=123, x_edit_summary="test")
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_lexeme_invalid_lexical_category_raises_error(self, mock_state: MagicMock) -> None:
        handler = self._make_handler(mock_state)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await handler.create_entity(
                self._make_request(lexical_category="invalid"),
                EditHeaders(x_user_id=123, x_edit_summary="test")
            )
        assert exc_info.value.status_code == 400
