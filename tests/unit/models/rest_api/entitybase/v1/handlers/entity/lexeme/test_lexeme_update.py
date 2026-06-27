"""Unit tests for EntityUpdateLexemeMixin in update_lexeme.py."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import LexemeUpdateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.update_lexeme import (
    EntityUpdateLexemeMixin,
)
from models.infrastructure.s3.exceptions import S3NotFoundError


class TestEntityUpdateLexemeMixin:
    """Unit tests for EntityUpdateLexemeMixin."""

    @pytest.fixture
    def mixin(self) -> EntityUpdateLexemeMixin:
        mock_state = MagicMock()
        return EntityUpdateLexemeMixin(state=mock_state)

    @pytest.mark.asyncio
    async def test_update_lexeme_invalid_entity_id_format(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        request = MagicMock(spec=LexemeUpdateRequest)
        edit_headers = EditHeaders(x_edit_summary="test")
        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_lexeme("Q42", request, edit_headers)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_lexeme_entity_not_found(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        mixin.state.mysql_client.entity_exists.return_value = False
        request = MagicMock(spec=LexemeUpdateRequest)
        edit_headers = EditHeaders(x_edit_summary="test")
        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_lexeme("L123", request, edit_headers)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_lexeme_entity_deleted(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = True
        request = MagicMock(spec=LexemeUpdateRequest)
        edit_headers = EditHeaders(x_edit_summary="test")
        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_lexeme("L123", request, edit_headers)
        assert exc_info.value.status_code == 410

    @pytest.mark.asyncio
    async def test_update_lexeme_entity_locked(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = False
        mixin.state.mysql_client.is_entity_locked.return_value = True
        request = MagicMock(spec=LexemeUpdateRequest)
        edit_headers = EditHeaders(x_edit_summary="test")
        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_lexeme("L123", request, edit_headers)
        assert exc_info.value.status_code == 423

    @pytest.mark.asyncio
    async def test_update_lexeme_success(self, mixin: EntityUpdateLexemeMixin) -> None:
        from models.data.rest_api.v1.entitybase.response import StatementHashResult

        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = False
        mixin.state.mysql_client.is_entity_locked.return_value = False
        mixin.state.mysql_client.get_head.return_value = 5

        mock_tx = MagicMock()
        mock_tx.process_lexeme_terms = MagicMock()
        mock_tx.process_statements.return_value = StatementHashResult(
            statements=[], labels={}, descriptions={}, aliases={}, sitelinks={}
        )
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 6
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event = AsyncMock()
        mock_tx.commit = MagicMock()

        mock_activity_result = MagicMock()
        mock_activity_result.success = True
        mixin.state.mysql_client.user_repository.log_user_activity = AsyncMock(
            return_value=mock_activity_result
        )

        mock_request_data = MagicMock()
        mock_request_data.forms = []
        mock_request_data.senses = []
        mock_request_data.lemmas = {}
        mock_request_data.id = "L123"
        mock_request_data.model_dump.return_value = {
            "id": "L123",
            "type": "lexeme",
            "forms": [],
            "senses": [],
            "lemmas": {},
        }

        request = MagicMock(spec=LexemeUpdateRequest)
        request.data.model_copy.return_value = mock_request_data
        request.type = "lexeme"

        edit_headers = EditHeaders(x_edit_summary="test update")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_lexeme.UpdateTransaction",
            return_value=mock_tx,
        ):
            result = await mixin.update_lexeme("L123", request, edit_headers)

        assert result == mock_response
        mock_tx.process_lexeme_terms.assert_called_once()
        mock_tx.create_revision.assert_awaited_once()
        mock_tx.publish_event.assert_awaited_once()
        mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_lexeme_s3_not_found_error(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = False
        mixin.state.mysql_client.is_entity_locked.return_value = False
        mixin.state.mysql_client.get_head.side_effect = S3NotFoundError("S3 error")

        mock_tx = MagicMock()
        mock_tx.state = mixin.state
        mock_tx.rollback = MagicMock()

        mock_request_data = MagicMock()
        mock_request_data.forms = []
        mock_request_data.senses = []
        mock_request_data.lemmas = {}
        mock_request_data.model_dump.return_value = {
            "id": "L123",
            "type": "lexeme",
            "forms": [],
            "senses": [],
            "lemmas": {},
        }

        request = MagicMock(spec=LexemeUpdateRequest)
        request.data.model_copy.return_value = mock_request_data
        request.type = "lexeme"

        edit_headers = EditHeaders(x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_lexeme.UpdateTransaction",
            return_value=mock_tx,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await mixin.update_lexeme("L123", request, edit_headers)
        assert exc_info.value.status_code == 404
        mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_lexeme_http_exception_rollback(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = False
        mixin.state.mysql_client.is_entity_locked.return_value = False
        mixin.state.mysql_client.get_head.return_value = 5

        mock_tx = MagicMock()
        mock_tx.process_lexeme_terms = MagicMock()
        mock_tx.process_statements.side_effect = HTTPException(
            status_code=400, detail="Bad request"
        )
        mock_tx.rollback = MagicMock()

        mock_request_data = MagicMock()
        mock_request_data.forms = []
        mock_request_data.senses = []
        mock_request_data.lemmas = {}
        mock_request_data.model_dump.return_value = {
            "id": "L123",
            "type": "lexeme",
            "forms": [],
            "senses": [],
            "lemmas": {},
        }

        request = MagicMock(spec=LexemeUpdateRequest)
        request.data.model_copy.return_value = mock_request_data
        request.type = "lexeme"

        edit_headers = EditHeaders(x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_lexeme.UpdateTransaction",
            return_value=mock_tx,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await mixin.update_lexeme("L123", request, edit_headers)
        assert exc_info.value.status_code == 400
        mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_lexeme_generic_exception_rollback(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = False
        mixin.state.mysql_client.is_entity_locked.return_value = False
        mixin.state.mysql_client.get_head.return_value = 5

        mock_tx = MagicMock()
        mock_tx.process_lexeme_terms = MagicMock()
        mock_tx.process_statements.side_effect = ValueError("Unexpected error")
        mock_tx.rollback = MagicMock()

        mock_request_data = MagicMock()
        mock_request_data.forms = []
        mock_request_data.senses = []
        mock_request_data.lemmas = {}
        mock_request_data.model_dump.return_value = {
            "id": "L123",
            "type": "lexeme",
            "forms": [],
            "senses": [],
            "lemmas": {},
        }

        request = MagicMock(spec=LexemeUpdateRequest)
        request.data.model_copy.return_value = mock_request_data
        request.type = "lexeme"

        edit_headers = EditHeaders(x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_lexeme.UpdateTransaction",
            return_value=mock_tx,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await mixin.update_lexeme("L123", request, edit_headers)
        assert exc_info.value.status_code == 500
        mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_lexeme_user_activity_logged(
        self, mixin: EntityUpdateLexemeMixin
    ) -> None:
        from models.data.rest_api.v1.entitybase.response import StatementHashResult

        mixin.state.mysql_client.entity_exists.return_value = True
        mixin.state.mysql_client.is_entity_deleted.return_value = False
        mixin.state.mysql_client.is_entity_locked.return_value = False
        mixin.state.mysql_client.get_head.return_value = 5

        mock_tx = MagicMock()
        mock_tx.process_lexeme_terms = MagicMock()
        mock_tx.process_statements.return_value = StatementHashResult(
            statements=[], labels={}, descriptions={}, aliases={}, sitelinks={}
        )
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 6
        mock_tx.create_revision = AsyncMock(return_value=mock_response)
        mock_tx.publish_event = AsyncMock()
        mock_tx.commit = MagicMock()

        mock_activity_result = MagicMock()
        mock_activity_result.success = True
        mixin.state.mysql_client.user_repository.log_user_activity = AsyncMock(
            return_value=mock_activity_result
        )

        mock_request_data = MagicMock()
        mock_request_data.forms = []
        mock_request_data.senses = []
        mock_request_data.lemmas = {}
        mock_request_data.model_dump.return_value = {
            "id": "L123",
            "type": "lexeme",
            "forms": [],
            "senses": [],
            "lemmas": {},
        }

        request = MagicMock(spec=LexemeUpdateRequest)
        request.data.model_copy.return_value = mock_request_data
        request.type = "lexeme"

        edit_headers = EditHeaders(x_edit_summary="test")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_lexeme.UpdateTransaction",
            return_value=mock_tx,
        ):
            await mixin.update_lexeme("L123", request, edit_headers)

        mixin.state.mysql_client.user_repository.log_user_activity.assert_awaited_once()
