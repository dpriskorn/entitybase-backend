"""Unit tests for lexemes forms and senses endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from src.models.rest_api.entitybase.v1.endpoints.lexemes import (
    _extract_numeric_suffix,
    _parse_form_id,
    _parse_sense_id,
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


class TestFormsAndSensesEndpoints:
    """Test form and sense endpoints."""

    @pytest.mark.asyncio
    async def test_get_lexeme_forms_returns_sorted_forms(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_forms

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {"id": "L42-F2", "representations": {"en": {"language": "en", "value": "form2"}}},
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "form1"}}},
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_forms("L42", mock_req)

        assert len(result.forms) == 2
        assert result.forms[0].id == "L42-F1"
        assert result.forms[1].id == "L42-F2"

    @pytest.mark.asyncio
    async def test_get_lexeme_senses_returns_sorted_senses(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_lexeme_senses

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "senses": [
                {"id": "L42-S2", "glosses": {"en": {"language": "en", "value": "gloss2"}}},
                {"id": "L42-S1", "glosses": {"en": {"language": "en", "value": "gloss1"}}},
            ],
            "forms": [],
        }
        mock_handler.get_entity.return_value = mock_entity

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_lexeme_senses("L42", mock_req)

        assert len(result.senses) == 2
        assert result.senses[0].id == "L42-S1"
        assert result.senses[1].id == "L42-S2"

    @pytest.mark.asyncio
    async def test_get_form_by_id_full_format(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_form_by_id

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "answer"}}}
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_form_by_id("L42-F1", mock_req)

        assert result.id == "L42-F1"
        assert "answer" in result.representations["en"].value

    @pytest.mark.asyncio
    async def test_get_form_by_id_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_form_by_id

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {"forms": [], "senses": []}
        mock_handler.get_entity.return_value = mock_entity

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_form_by_id("L42-F99", mock_req)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_sense_by_id_full_format(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_by_id

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "senses": [
                {"id": "L42-S1", "glosses": {"en": {"language": "en", "value": "reply"}}}
            ],
            "forms": [],
        }
        mock_handler.get_entity.return_value = mock_entity

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_sense_by_id("L42-S1", mock_req)

        assert result.id == "L42-S1"
        assert "reply" in result.glosses["en"].value

    @pytest.mark.asyncio
    async def test_get_sense_by_id_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_by_id

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {"forms": [], "senses": []}
        mock_handler.get_entity.return_value = mock_entity

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_sense_by_id("L42-S99", mock_req)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_form_representations(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_form_representations

        mock_form_response = Mock()
        mock_form_response.model_dump.return_value = {
            "representations": {
                "en": {"language": "en", "value": "answer"},
                "de": {"language": "de", "value": "Antwort"},
            }
        }

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.get_form_by_id",
            new=AsyncMock(return_value=mock_form_response)
        ):
            mock_req = Mock()
            result = await get_form_representations("L42-F1", mock_req)

            assert "en" in result
            assert result["en"]["value"] == "answer"
            assert "de" in result

    @pytest.mark.asyncio
    async def test_get_form_representation_specific_language(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_form_representation

        mock_form_response = Mock()
        mock_form_response.representations = {
            "en": Mock(language="en", value="answer"),
            "de": Mock(language="de", value="Antwort"),
        }

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.get_form_by_id",
            new=AsyncMock(return_value=mock_form_response)
        ):
            mock_req = Mock()
            result = await get_form_representation("L42-F1", "en", mock_req)

            assert result["value"] == "answer"

    @pytest.mark.asyncio
    async def test_get_form_representation_language_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_form_representation

        mock_form_response = Mock()
        mock_form_response.representations = {"en": Mock(language="en", value="answer")}

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.get_form_by_id",
            new=AsyncMock(return_value=mock_form_response)
        ):
            mock_req = Mock()

            with pytest.raises(HTTPException) as exc:
                await get_form_representation("L42-F1", "fr", mock_req)

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_sense_glosses(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_glosses

        mock_sense_response = Mock()
        mock_sense_response.model_dump.return_value = {
            "glosses": {
                "en": {"language": "en", "value": "reply; reaction"},
                "de": {"language": "de", "value": "Antwort"},
            }
        }

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.get_sense_by_id",
            new=AsyncMock(return_value=mock_sense_response)
        ):
            mock_req = Mock()
            result = await get_sense_glosses("L42-S1", mock_req)

            assert "en" in result
            assert result["en"]["value"] == "reply; reaction"
            assert "de" in result

    @pytest.mark.asyncio
    async def test_get_sense_gloss_specific_language(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_gloss

        mock_sense_response = Mock()
        mock_sense_response.glosses = {
            "en": Mock(language="en", value="reply; reaction"),
            "de": Mock(language="de", value="Antwort"),
        }

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.get_sense_by_id",
            new=AsyncMock(return_value=mock_sense_response)
        ):
            mock_req = Mock()
            result = await get_sense_gloss("L42-S1", "en", mock_req)

            assert result["value"] == "reply; reaction"

    @pytest.mark.asyncio
    async def test_get_sense_gloss_language_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_gloss

        mock_sense_response = Mock()
        mock_sense_response.glosses = {"en": Mock(language="en", value="reply")}

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.get_sense_by_id",
            new=AsyncMock(return_value=mock_sense_response)
        ):
            mock_req = Mock()

            with pytest.raises(HTTPException) as exc:
                await get_sense_gloss("L42-S1", "fr", mock_req)

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_form_representation_missing_language(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import update_form_representation

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "answer"}}}
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await update_form_representation(
                "L42-F1",
                "fr",
                {"value": "réponse"},
                mock_req,
                edit_summary="test edit"
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_form_representation_invalid_data(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import update_form_representation

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "answer"}}}
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await update_form_representation(
                "L42-F1",
                "en",
                {},  # Missing 'value' field
                mock_req,
                edit_summary="test edit"
            )

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_form_id_short_format_not_implemented(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_form_by_id

        mock_req = Mock()

        with pytest.raises(HTTPException) as exc:
            await get_form_by_id("F1", mock_req)

        assert exc.value.status_code == 400
        assert "short format" in str(exc.value.detail).lower()

    @pytest.mark.asyncio
    async def test_sense_id_short_format_not_implemented(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import get_sense_by_id

        mock_req = Mock()

        with pytest.raises(HTTPException) as exc:
            await get_sense_by_id("S1", mock_req)

        assert exc.value.status_code == 400
        assert "short format" in str(exc.value.detail).lower()

    @pytest.mark.asyncio
    async def test_delete_form_representation(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_form_representation

        mock_state = Mock()
        mock_handler = Mock()
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.entity_data = {
            "forms": [
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "answer"}}}
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state
        mock_state.validator = Mock()
        mock_update_handler.update_entity = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.LexemeUpdateHandler",
            return_value=mock_update_handler
        ):
            await delete_form_representation(
                "L42-F1",
                "en",
                mock_req,
                edit_summary="remove representation"
            )

            # Check representation was removed
            assert "en" not in mock_entity.entity_data["forms"][0]["representations"]

    @pytest.mark.asyncio
    async def test_delete_form_representation_language_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_form_representation

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.entity_data = {
            "forms": [
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "answer"}}}
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_form_representation(
                "L42-F1",
                "fr",
                mock_req,
                edit_summary="remove representation"
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_form_representation_form_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_form_representation

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {"forms": [], "senses": []}
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_form_representation(
                "L42-F99",
                "en",
                mock_req,
                edit_summary="remove representation"
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_sense_gloss(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_sense_gloss

        mock_state = Mock()
        mock_handler = Mock()
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.data = {
            "senses": [
                {"id": "L42-S1", "glosses": {"en": {"language": "en", "value": "reply"}}}
            ],
            "forms": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state
        mock_state.validator = Mock()
        mock_update_handler.update_entity = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.LexemeUpdateHandler",
            return_value=mock_update_handler
        ):
            await delete_sense_gloss(
                "L42-S1",
                "en",
                mock_req,
                edit_summary="remove gloss"
            )

            # Check gloss was removed
            assert "en" not in mock_entity.data["senses"][0]["glosses"]

    @pytest.mark.asyncio
    async def test_delete_sense_gloss_not_found_idempotent(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_sense_gloss

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {
            "senses": [
                {"id": "L42-S1", "glosses": {"en": {"language": "en", "value": "reply"}}}
            ],
            "forms": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await delete_sense_gloss(
            "L42-S1",
            "fr",
            mock_req,
            edit_summary="remove gloss"
        )

        # Should return current entity idempotently
        assert result.id == mock_entity.id

    @pytest.mark.asyncio
    async def test_delete_sense_gloss_sense_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_sense_gloss

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {"senses": [], "forms": []}
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_sense_gloss(
                "L42-S99",
                "en",
                mock_req,
                edit_summary="remove gloss"
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_form(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_form

        mock_state = Mock()
        mock_handler = Mock()
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.data = {
            "forms": [
                {"id": "L42-F1", "representations": {"en": {"language": "en", "value": "answer"}}},
                {"id": "L42-F2", "representations": {"en": {"language": "en", "value": "form2"}}},
            ],
            "senses": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state
        mock_state.validator = Mock()
        mock_update_handler.update_entity = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.LexemeUpdateHandler",
            return_value=mock_update_handler
        ):
            await delete_form(
                "L42-F1",
                mock_req,
                edit_summary="remove form"
            )

            # Check form was removed
            assert len(mock_entity.data["forms"]) == 1
            assert mock_entity.data["forms"][0]["id"] == "L42-F2"

    @pytest.mark.asyncio
    async def test_delete_form_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_form

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {"forms": [], "senses": []}
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_form(
                "L42-F99",
                mock_req,
                edit_summary="remove form"
            )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_sense(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_sense

        mock_state = Mock()
        mock_handler = Mock()
        mock_update_handler = AsyncMock()
        mock_entity = Mock()
        mock_entity.data = {
            "senses": [
                {"id": "L42-S1", "glosses": {"en": {"language": "en", "value": "reply"}}},
                {"id": "L42-S2", "glosses": {"en": {"language": "en", "value": "meaning2"}}},
            ],
            "forms": [],
        }
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state
        mock_state.validator = Mock()
        mock_update_handler.update_entity = AsyncMock(return_value=mock_entity)

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.mock.patch(
            "src.models.rest_api.entitybase.v1.endpoints.lexemes.LexemeUpdateHandler",
            return_value=mock_update_handler
        ):
            await delete_sense(
                "L42-S1",
                mock_req,
                edit_summary="remove sense"
            )

            # Check sense was removed
            assert len(mock_entity.data["senses"]) == 1
            assert mock_entity.data["senses"][0]["id"] == "L42-S2"

    @pytest.mark.asyncio
    async def test_delete_sense_not_found(self):
        from src.models.rest_api.entitybase.v1.endpoints.lexemes import delete_sense

        mock_state = Mock()
        mock_handler = Mock()
        mock_entity = Mock()
        mock_entity.data = {"senses": [], "forms": []}
        mock_handler.get_entity.return_value = mock_entity
        mock_state.state_handler = mock_state

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await delete_sense(
                "L42-S99",
                mock_req,
                edit_summary="remove sense"
            )

        assert exc.value.status_code == 404
