"""Unit tests for lexemes forms and senses endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from models.rest_api.entitybase.v1.endpoints.lexemes import (
    _extract_numeric_suffix,
    _parse_form_id,
    _parse_sense_id,
    _validate_qid,
    delete_form_representation,
    delete_sense_gloss,
)


class TestFormAndSenseHelpers:
    """Test helper functions for form/sense ID parsing."""

    def test_parse_form_id_full_format(self):
        result = _parse_form_id("L42-F1")
        assert result == ("L42", "F1")

    def test_parse_form_id_short_format(self):
        result = _parse_form_id("F12")
        assert result == ("", "F12")

    def test_parse_form_id_invalid_format(self):
        with pytest.raises(HTTPException) as exc:
            _parse_form_id("invalid-id")
        assert exc.value.status_code == 400

    def test_parse_sense_id_full_format(self):
        result = _parse_sense_id("L42-S1")
        assert result == ("L42", "S1")

    def test_parse_sense_id_short_format(self):
        result = _parse_sense_id("S12")
        assert result == ("", "S12")

    def test_parse_sense_id_invalid_format(self):
        with pytest.raises(HTTPException) as exc:
            _parse_sense_id("invalid-id")
        assert exc.value.status_code == 400

    def test_extract_numeric_suffix(self):
        assert _extract_numeric_suffix("F1") == 1
        assert _extract_numeric_suffix("F12") == 12
        assert _extract_numeric_suffix("S1") == 1
        assert _extract_numeric_suffix("S42") == 42


class TestQidValidation:
    """Test QID validation helper."""

    def test_validate_qid_valid_qid(self):
        result = _validate_qid("Q1860", "language")
        assert result == "Q1860"

    def test_validate_qid_valid_qid_large_number(self):
        result = _validate_qid("Q123456789", "lexical_category")
        assert result == "Q123456789"

    def test_validate_qid_empty_string(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("", "language")
        assert exc.value.status_code == 400
        assert "required" in exc.value.detail.lower()

    def test_validate_qid_invalid_format_no_q(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("1860", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail

    def test_validate_qid_invalid_format_lowercase(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("q1860", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail

    def test_validate_qid_invalid_format_no_digits(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("Q", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail

    def test_validate_qid_invalid_format_letters(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("Qabc", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail


class TestLanguageEndpoints:
    """Test language GET/PUT endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_language(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_language
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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
        from models.data.infrastructure.s3 import S3RevisionData

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


class TestFormsAndSensesEndpoints:
    """Test form and sense endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_forms_returns_sorted_forms(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_forms
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "forms": [
                    {
                        "id": "L42-F2",
                        "representations": {"en": {"language": "en", "value": "form2"}},
                    },
                    {
                        "id": "L42-F1",
                        "representations": {"en": {"language": "en", "value": "form1"}},
                    },
                ],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_forms("L42", mock_req)

        assert len(result.forms) == 2
        assert result.forms[0].id == "L42-F1"
        assert result.forms[1].id == "L42-F2"

    @pytest.mark.asyncio
    async def test_get_lexeme_senses_returns_sorted_senses(
        self, mock_entity_read_state
    ):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_senses
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "senses": [
                    {
                        "id": "L42-S2",
                        "glosses": {"en": {"language": "en", "value": "gloss2"}},
                    },
                    {
                        "id": "L42-S1",
                        "glosses": {"en": {"language": "en", "value": "gloss1"}},
                    },
                ],
                "forms": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_senses("L42", mock_req)

        assert len(result.senses) == 2
        assert result.senses[0].id == "L42-S1"
        assert result.senses[1].id == "L42-S2"

    @pytest.mark.asyncio
    async def test_get_form_by_id_full_format(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_form_by_id
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "forms": [
                    {
                        "id": "L42-F1",
                        "representations": {
                            "en": {"language": "en", "value": "answer"}
                        },
                    }
                ],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_form_by_id("L42-F1", mock_req)

        assert result.id == "L42-F1"
        assert "answer" in result.representations["en"].value

    @pytest.mark.asyncio
    async def test_get_form_by_id_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_form_by_id
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"forms": [], "senses": []},
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_form_by_id("L42-F99", mock_req)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_sense_by_id_full_format(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_by_id
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "senses": [
                    {
                        "id": "L42-S1",
                        "glosses": {"en": {"language": "en", "value": "reply"}},
                    }
                ],
                "forms": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_sense_by_id("L42-S1", mock_req)

        assert result.id == "L42-S1"
        assert "reply" in result.glosses["en"].value

    @pytest.mark.asyncio
    async def test_get_sense_by_id_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_by_id
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"forms": [], "senses": []},
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_sense_by_id("L42-S99", mock_req)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_form_representation_missing_language(
        self, mock_entity_read_state
    ):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_form_representation,
        )
        from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "forms": [
                    {
                        "id": "L42-F1",
                        "representations": {
                            "en": {"language": "en", "value": "answer"}
                        },
                    }
                ],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await update_form_representation(
                "L42-F1",
                "en",
                TermUpdateRequest(language="fr", value="réponse"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="test edit"),
            )

        assert exc.value.status_code == 400
        assert "does not match" in exc.value.detail

    @pytest.mark.asyncio
    async def test_update_form_representation_language_mismatch(
        self, mock_entity_read_state
    ):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_form_representation,
        )
        from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "forms": [
                    {
                        "id": "L42-F1",
                        "representations": {
                            "en": {"language": "en", "value": "answer"}
                        },
                    }
                ],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await update_form_representation(
                "L42-F1",
                "en",
                TermUpdateRequest(language="fr", value="réponse"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="test edit"),
            )

        assert exc.value.status_code == 400
        assert "does not match" in exc.value.detail

    @pytest.mark.asyncio
    async def test_form_id_short_format_not_implemented(self):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_form_by_id

        mock_req = Mock()

        with pytest.raises(HTTPException) as exc:
            await get_form_by_id("F1", mock_req)

        assert exc.value.status_code == 400
        assert "short format" in str(exc.value.detail).lower()

    @pytest.mark.asyncio
    async def test_sense_id_short_format_not_implemented(self):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_by_id

        mock_req = Mock()

        with pytest.raises(HTTPException) as exc:
            await get_sense_by_id("S1", mock_req)


class TestLemmasEndpoints:
    """Test lemma endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_lemmas(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_lemmas
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lemmas": {
                    "en": {"language": "en", "value": "answer"},
                    "de": {"language": "de", "value": "Antwort"},
                },
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_lemmas("L42", mock_req)

        assert "en" in result.lemmas
        assert "de" in result.lemmas
        assert result.lemmas["en"].value == "answer"
        assert result.lemmas["de"].value == "Antwort"

    @pytest.mark.asyncio
    async def test_get_lexeme_lemma_by_language(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_lemma
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lemmas": {"en": {"language": "en", "value": "answer"}},
                "forms": [],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_lemma("L42", "en", mock_req)

        assert result.value == "answer"

    @pytest.mark.asyncio
    async def test_get_lexeme_lemma_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_lemma
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lemmas": {"en": {"language": "en", "value": "answer"}},
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
            await get_lexeme_lemma("L42", "de", mock_req)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_delete_lexeme_lemma_last_lemma_fails(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import delete_lexeme_lemma
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "lemmas": {"en": {"language": "en", "value": "answer"}},
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
            await delete_lexeme_lemma(
                "L42",
                "en",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="test edit"),
            )

        assert exc.value.status_code == 400
        assert "at least one lemma" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_form_representation(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import (
            update_form_representation,
        )
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {
                    "id": "L42-F1",
                    "representations": {"en": {"language": "en", "value": "answer"}},
                }
            ],
            "senses": [],
        }

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "forms": [
                    {
                        "id": "L42-F1",
                        "representations": {
                            "en": {"language": "en", "value": "answer"}
                        },
                    }
                ],
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
            result = await update_form_representation(
                "L42-F1",
                "en",
                Mock(language="en", value="new value"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="test"),
            )

            # Check update_lexeme was called
            assert mock_update_handler.update_lexeme.called

    @pytest.mark.asyncio
    async def test_delete_form_representation_language_not_found(
        self, mock_entity_read_state
    ):
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {
                    "id": "L42-F1",
                    "representations": {"en": {"language": "en", "value": "answer"}},
                }
            ],
            "senses": [],
        }

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "forms": [
                    {
                        "id": "L42-F1",
                        "representations": {
                            "en": {"language": "en", "value": "answer"}
                        },
                    }
                ],
                "senses": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_form_representation(
                "L42-F1",
                "fr",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="remove representation"),
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_form_representation_form_not_found(
        self, mock_entity_read_state
    ):
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"forms": [], "senses": []},
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_form_representation(
                "L42-F99",
                "en",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="remove representation"),
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_sense_gloss_not_found_idempotent(
        self, mock_entity_read_state
    ):
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state
        mock_entity = Mock()
        mock_entity.id = "L42"
        mock_entity.data = {
            "senses": [
                {
                    "id": "L42-S1",
                    "glosses": {"en": {"language": "en", "value": "reply"}},
                }
            ],
            "forms": [],
        }

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "senses": [
                    {
                        "id": "L42-S1",
                        "glosses": {"en": {"language": "en", "value": "reply"}},
                    }
                ],
                "forms": [],
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await delete_sense_gloss(
            "L42-S1",
            "fr",
            mock_req,
            headers=Mock(x_user_id=123, x_edit_summary="remove gloss"),
        )

        # Should return current entity idempotently
        assert result.id == mock_entity.id

    @pytest.mark.asyncio
    async def test_delete_sense_gloss_sense_not_found(self, mock_entity_read_state):
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"senses": [], "forms": []},
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_sense_gloss(
                "L42-S99",
                "en",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="remove gloss"),
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_form_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import delete_form
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"forms": [], "senses": []},
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_form(
                "L42-F99",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="remove form"),
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_sense_not_found(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import delete_sense
        from models.data.infrastructure.s3 import S3RevisionData

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"senses": [], "forms": []},
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_state.validator = Mock()

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_sense(
                "L42-S99",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="remove sense"),
            )

        assert exc.value.status_code == 404
