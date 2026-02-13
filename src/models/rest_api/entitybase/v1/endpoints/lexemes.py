"""Lexeme endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
    LexemeUpdateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    LemmaResponse,
    LemmasResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/lexemes", response_model=EntityResponse)
async def create_lexeme(
    request: EntityCreateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Create a new lexeme entity."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator
    enumeration_service = req.app.state.state_handler.enumeration_service
    handler = LexemeCreateHandler(enumeration_service=enumeration_service, state=state)
    return await handler.create_entity(  # type: ignore[no-any-return]
        request=request,
        edit_headers=headers,
        validator=validator,
    )


@router.get("/entities/lexemes/{lexeme_id}/lemmas", response_model=LemmasResponse)
async def get_lexeme_lemmas(lexeme_id: str, req: Request) -> LemmasResponse:
    """Get all lemmas for a lexeme."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    lemmas_data = entity.entity_data.revision.get("lemmas", {})

    from models.data.rest_api.v1.entitybase.response.lexemes import RepresentationData

    lemmas = {
        lang: RepresentationData(language=lang, value=data["value"])
        for lang, data in lemmas_data.items()
        if lang != "lemma_hashes" and "value" in data
    }
    return LemmasResponse(lemmas=lemmas)


@router.get(
    "/entities/lexemes/{lexeme_id}/lemmas/{langcode}",
    response_model=LemmaResponse,
)
async def get_lexeme_lemma(
    lexeme_id: str, langcode: str, req: Request
) -> LemmaResponse:
    """Get lemma for a lexeme in specific language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    lemmas_data = entity.entity_data.revision.get("lemmas", {})

    lemma = lemmas_data.get(langcode)
    if not lemma or "value" not in lemma:
        raise HTTPException(
            status_code=404, detail=f"Lemma not found for language {langcode}"
        )
    return LemmaResponse(value=lemma["value"])


@router.post(
    "/entities/lexemes/{lexeme_id}/lemmas/{langcode}",
    response_model=EntityResponse,
)
async def add_lexeme_lemma(
    lexeme_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Add a new lemma for language."""
    logger.debug(f"Adding lemma for lexeme {lexeme_id}, language {langcode}")

    if request.language != langcode:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({langcode})",
        )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    lemmas_data = current_entity.entity_data.revision.get("lemmas", {})
    if langcode in lemmas_data:
        raise HTTPException(
            status_code=409,
            detail=f"Lemma already exists for language {langcode}. Use PUT to update.",
        )

    lemmas_data[langcode] = {"language": langcode, "value": request.value}

    logger.debug(f"Added lemma for lexeme {lexeme_id} in language {langcode}")

    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(
        id=lexeme_id, type="lexeme", **current_entity.entity_data.revision
    )

    return await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )


@router.put(
    "/entities/lexemes/{lexeme_id}/lemmas/{langcode}",
    response_model=EntityResponse,
)
async def update_lexeme_lemma(
    lexeme_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update lemma for language."""
    logger.debug(f"Updating lemma for lexeme {lexeme_id}, language {langcode}")

    if request.language != langcode:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({langcode})",
        )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    lemmas_data = current_entity.entity_data.revision.get("lemmas", {})
    if langcode in lemmas_data:
        lemmas_data[langcode]["value"] = request.value
    else:
        lemmas_data[langcode] = {"language": langcode, "value": request.value}

    logger.debug(f"Updated lemma value for lexeme {lexeme_id} in language {langcode}")

    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(
        id=lexeme_id, type="lexeme", **current_entity.entity_data.revision
    )

    return await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )


@router.delete(
    "/entities/lexemes/{lexeme_id}/lemmas/{langcode}",
    response_model=EntityResponse,
)
async def delete_lexeme_lemma(
    lexeme_id: str,
    langcode: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete lemma for language."""
    logger.debug(f"Deleting lemma for lexeme {lexeme_id}, language {langcode}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    lemmas_data = current_entity.entity_data.revision.get("lemmas", {})

    if langcode not in lemmas_data:
        return current_entity

    current_lemma_count = sum(1 for lang in lemmas_data if lang != "lemma_hashes")

    if current_lemma_count == 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the last lemma. A lexeme must have at least one lemma.",
        )

    del lemmas_data[langcode]
    logger.debug(f"Deleted lemma for lexeme {lexeme_id} in language {langcode}")

    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(
        id=lexeme_id, type="lexeme", **current_entity.entity_data.revision
    )

    return await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )
