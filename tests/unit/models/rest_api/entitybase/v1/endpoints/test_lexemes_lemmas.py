"""Unit tests for lexeme lemmas endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3 import S3RevisionData


class TestLemmasEndpoints:
    """Test lemma endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_lemmas(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_lemmas

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


class TestFormRepresentationUpdates:
    """Test form representation update operations."""

    @pytest.mark.asyncio
    async def test_update_form_representation(self, mock_entity_read_state):
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
            "models.rest_api.entitybase.v1.endpoints.lexeme_forms.EntityUpdateHandler",
            return_value=mock_update_handler,
        ):
            from models.rest_api.entitybase.v1.endpoints.lexeme_forms import (
                update_form_representation,
            )

            result = await update_form_representation(
                "L42-F1",
                "en",
                Mock(language="en", value="new value"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="test"),
            )

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
            from models.rest_api.entitybase.v1.endpoints.lexeme_forms import (
                delete_form_representation,
            )

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import (
            delete_form_representation,
        )

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            delete_sense_gloss,
        )

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

        assert result.success is True

    @pytest.mark.asyncio
    async def test_delete_sense_gloss_sense_not_found(self, mock_entity_read_state):
        from models.data.infrastructure.s3 import S3RevisionData
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            delete_sense_gloss,
        )

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
    async def test_delete_sense_gloss_last_gloss_fails(self, mock_entity_read_state):
        from models.data.infrastructure.s3 import S3RevisionData
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            delete_sense_gloss,
        )

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

        with pytest.raises(HTTPException) as exc:
            await delete_sense_gloss(
                "L42-S1",
                "en",
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="remove gloss"),
            )

        assert exc.value.status_code == 400
        assert "cannot have 0 glosses" in exc.value.detail

    @pytest.mark.asyncio
    async def test_add_sense_gloss(self, mock_entity_read_state):
        from models.data.infrastructure.s3 import S3RevisionData
        from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            add_sense_gloss,
        )

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

        mock_state.validator = Mock()
        mock_update_handler = AsyncMock()
        mock_update_handler.update_lexeme = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with patch(
            "models.rest_api.entitybase.v1.endpoints.lexeme_forms.EntityUpdateHandler",
            return_value=mock_update_handler,
        ):
            result = await add_sense_gloss(
                "L42-S1",
                "de",
                TermUpdateRequest(language="de", value="Antwort"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="add gloss"),
            )

        assert result.hash is not None

    @pytest.mark.asyncio
    async def test_add_sense_gloss_already_exists(self, mock_entity_read_state):
        from models.data.infrastructure.s3 import S3RevisionData
        from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            add_sense_gloss,
        )

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

        mock_state.validator = Mock()

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await add_sense_gloss(
                "L42-S1",
                "en",
                TermUpdateRequest(language="en", value="reply"),
                mock_req,
                headers=Mock(x_user_id=123, x_edit_summary="add gloss"),
            )

        assert exc.value.status_code == 409
        assert "already exists" in exc.value.detail

    @pytest.mark.asyncio
    async def test_delete_form_not_found(self, mock_entity_read_state):
        from models.data.infrastructure.s3 import S3RevisionData
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import delete_form

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
        from models.data.infrastructure.s3 import S3RevisionData
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import delete_sense

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
