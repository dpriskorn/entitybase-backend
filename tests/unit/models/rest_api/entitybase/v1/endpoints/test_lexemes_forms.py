"""Unit tests for lexeme forms and senses endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3 import S3RevisionData


class TestFormsAndSensesEndpoints:
    """Test form and sense endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_forms_returns_sorted_forms(self, mock_entity_read_state):
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import (
            get_lexeme_forms,
        )

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            get_lexeme_senses,
        )

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import get_form_by_id

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import get_form_by_id

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            get_sense_by_id,
        )

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            get_sense_by_id,
        )

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import (
            update_form_representation,
        )
        from models.data.rest_api.v1.entitybase.request import TermUpdateRequest

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import (
            update_form_representation,
        )
        from models.data.rest_api.v1.entitybase.request import TermUpdateRequest

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
        from models.rest_api.entitybase.v1.endpoints.lexeme_forms import get_form_by_id

        mock_req = Mock()

        with pytest.raises(HTTPException) as exc:
            await get_form_by_id("F1", mock_req)

        assert exc.value.status_code == 400
        assert "short format" in str(exc.value.detail).lower()

    @pytest.mark.asyncio
    async def test_sense_id_short_format_not_implemented(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_senses import (
            get_sense_by_id,
        )

        mock_req = Mock()

        with pytest.raises(HTTPException) as exc:
            await get_sense_by_id("S1", mock_req)
