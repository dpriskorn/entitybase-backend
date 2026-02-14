"""Lexeme endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Request

from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
    LexemeLanguageRequest,
    LexemeLexicalCategoryRequest,
    LexemeUpdateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    LemmaResponse,
    LemmasResponse,
    LexemeLanguageResponse,
    LexemeLexicalCategoryResponse,
    TermHashResponse,
    DeleteResponse,
)
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
    _extract_numeric_suffix,
    _parse_form_id,
    _parse_sense_id,
)

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.rest_api.utils import validate_qid

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
    return await handler.create_entity(
        request=request,
        edit_headers=headers,
        validator=validator,
    )


@router.get(
    "/entities/lexemes/{lexeme_id}/language", response_model=LexemeLanguageResponse
)
async def get_lexeme_language(lexeme_id: str, req: Request) -> LexemeLanguageResponse:
    """Get the language of a lexeme."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    language = entity.entity_data.revision.get("language", "")
    if not language:
        raise HTTPException(
            status_code=404, detail=f"Language not found for lexeme {lexeme_id}"
        )
    return LexemeLanguageResponse(language=language)


@router.put("/entities/lexemes/{lexeme_id}/language", response_model=EntityResponse)
async def update_lexeme_language(
    lexeme_id: str,
    request: LexemeLanguageRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update the language of a lexeme."""
    logger.debug(f"Updating language for lexeme {lexeme_id}")

    validate_qid(request.language, "language")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    revision_data = dict(current_entity.entity_data.revision)
    revision_data["language"] = request.language

    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(id=lexeme_id, type="lexeme", **revision_data)

    return await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )


@router.get(
    "/entities/lexemes/{lexeme_id}/lexicalcategory",
    response_model=LexemeLexicalCategoryResponse,
)
async def get_lexeme_lexicalcategory(
    lexeme_id: str, req: Request
) -> LexemeLexicalCategoryResponse:
    """Get the lexical category of a lexeme."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    lexical_category = entity.entity_data.revision.get("lexical_category", "")
    if not lexical_category:
        lexical_category = entity.entity_data.revision.get("lexicalCategory", "")
    if not lexical_category:
        raise HTTPException(
            status_code=404,
            detail=f"Lexical category not found for lexeme {lexeme_id}",
        )
    return LexemeLexicalCategoryResponse(lexical_category=lexical_category)


@router.put(
    "/entities/lexemes/{lexeme_id}/lexicalcategory", response_model=EntityResponse
)
async def update_lexeme_lexicalcategory(
    lexeme_id: str,
    request: LexemeLexicalCategoryRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update the lexical category of a lexeme."""
    logger.debug(f"Updating lexical category for lexeme {lexeme_id}")

    validate_qid(request.lexical_category, "lexical_category")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    revision_data = dict(current_entity.entity_data.revision)
    revision_data["lexical_category"] = request.lexical_category

    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(id=lexeme_id, type="lexeme", **revision_data)

    return await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )


@router.get("/entities/lexemes/{lexeme_id}/lemmas", response_model=LemmasResponse)
async def get_lexeme_lemmas(lexeme_id: str, req: Request) -> LemmasResponse:
    """Get all lemmas for a lexeme."""
    from models.data.rest_api.v1.entitybase.response.lexemes import RepresentationData

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    lemmas_data = entity.entity_data.revision.get("lemmas", {})

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
    response_model=TermHashResponse,
)
async def add_lexeme_lemma(
    lexeme_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
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

    await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )

    hash_value = MetadataExtractor.hash_string(request.value)
    return TermHashResponse(hash=hash_value)


@router.put(
    "/entities/lexemes/{lexeme_id}/lemmas/{langcode}",
    response_model=TermHashResponse,
)
async def update_lexeme_lemma(
    lexeme_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
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

    await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )

    hash_value = MetadataExtractor.hash_string(request.value)
    return TermHashResponse(hash=hash_value)


@router.delete(
    "/entities/lexemes/{lexeme_id}/lemmas/{langcode}",
    response_model=DeleteResponse,
)
async def delete_lexeme_lemma(
    lexeme_id: str,
    langcode: str,
    req: Request,
    headers: EditHeadersType,
) -> DeleteResponse:
    """Delete lemma for language."""
    logger.debug(f"Deleting lemma for lexeme {lexeme_id}, language {langcode}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    lemmas_data = current_entity.entity_data.revision.get("lemmas", {})

    if langcode not in lemmas_data:
        return DeleteResponse(success=True)

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

    await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )

    return DeleteResponse(success=True)
