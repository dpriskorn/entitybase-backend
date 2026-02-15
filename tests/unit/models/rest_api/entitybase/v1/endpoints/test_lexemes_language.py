"""Unit tests for lexeme language and lexical category endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3 import S3RevisionData


class TestLanguageEndpoints:
    """Test language GET/PUT endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_language(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_language

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "language": "Q1860",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_language("L42", mock_req)

        assert result.language == "Q1860"

    @pytest.mark.asyncio
    async def test_get_lexeme_language_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_language

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "language": "",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_lexeme_language("L42", mock_req)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_lexeme_language_valid(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_lexeme_language,
        )
        from models.data.rest_api.v1.entitybase.request import LexemeLanguageRequest

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.id = "L42"

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "language": "Q1860",
                "lexical_category": "Q1084",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()
        mock_update_handler.update_lexeme = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with patch(
            "models.rest_api.entitybase.v1.endpoints.lexemes.EntityUpdateHandler",
            return_value=mock_update_handler,
        ):
            await update_lexeme_language(
                "L42",
                LexemeLanguageRequest(language="Q150"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="change language"),
            )

            assert mock_update_handler.update_lexeme.called
            call_args = mock_update_handler.update_lexeme.call_args
            update_request = call_args[0][1]
            assert update_request.language == "Q150"

    @pytest.mark.asyncio
    async def test_update_lexeme_language_invalid_qid(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_lexeme_language,
        )
        from models.data.rest_api.v1.entitybase.request import LexemeLanguageRequest

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "language": "Q1860",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await update_lexeme_language(
                "L42",
                LexemeLanguageRequest(language="invalid"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="change language"),
            )

        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail


class TestLexicalCategoryEndpoints:
    """Test lexical category GET/PUT endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_lexicalcategory(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            get_lexeme_lexicalcategory,
        )

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lexical_category": "Q1084",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_lexicalcategory("L42", mock_req)

        assert result.lexical_category == "Q1084"

    @pytest.mark.asyncio
    async def test_get_lexeme_lexicalcategory_with_camel_case_fallback(
        self, mock_entity_read_state
    ):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            get_lexeme_lexicalcategory,
        )

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lexicalCategory": "Q1084",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_lexicalcategory("L42", mock_req)

        assert result.lexical_category == "Q1084"

    @pytest.mark.asyncio
    async def test_get_lexeme_lexicalcategory_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            get_lexeme_lexicalcategory,
        )

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lexical_category": "",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_lexeme_lexicalcategory("L42", mock_req)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_lexeme_lexicalcategory_valid(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_lexeme_lexicalcategory,
        )
        from models.data.rest_api.v1.entitybase.request import (
            LexemeLexicalCategoryRequest,
        )

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.id = "L42"

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "language": "Q1860",
                "lexical_category": "Q1084",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()
        mock_update_handler.update_lexeme = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with patch(
            "models.rest_api.entitybase.v1.endpoints.lexemes.EntityUpdateHandler",
            return_value=mock_update_handler,
        ):
            await update_lexeme_lexicalcategory(
                "L42",
                LexemeLexicalCategoryRequest(lexical_category="Q24905"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="change category"),
            )

            assert mock_update_handler.update_lexeme.called
            call_args = mock_update_handler.update_lexeme.call_args
            update_request = call_args[0][1]
            assert update_request.lexical_category == "Q24905"

    @pytest.mark.asyncio
    async def test_update_lexeme_lexicalcategory_invalid_qid(
        self, mock_entity_read_state
    ):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_lexeme_lexicalcategory,
        )
        from models.data.rest_api.v1.entitybase.request import (
            LexemeLexicalCategoryRequest,
        )

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lexical_category": "Q1084",
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await update_lexeme_lexicalcategory(
                "L42",
                LexemeLexicalCategoryRequest(lexical_category="not-a-qid"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="change category"),
            )

        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail
