"""Lexeme endpoints for Entitybase v1 API."""

import logging
import re

from fastapi import APIRouter, HTTPException, Request

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
)
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType

logger = logging.getLogger(__name__)

router = APIRouter()


def _extract_numeric_suffix(form_id: str) -> int:
    """Extract numeric suffix from form/sense ID (e.g., F1 -> 1, S42 -> 42)."""
    match = re.search(r"\d+$", form_id)
    if match:
        return int(match.group())
    raise HTTPException(status_code=400, detail=f"Invalid format: {form_id}")


def _parse_form_id(form_id: str) -> tuple[str, str]:
    """Parse form ID into (lexeme_id, form_id) components."""
    if "-" in form_id:
        parts = form_id.split("-")
        if len(parts) == 2 and parts[0].startswith("L") and parts[1].startswith("F"):
            return parts[0], parts[1]
    elif form_id.startswith("F"):
        return "", form_id
    raise HTTPException(status_code=400, detail=f"Invalid form ID format: {form_id}")


def _parse_sense_id(sense_id: str) -> tuple[str, str]:
    """Parse sense ID into (lexeme_id, sense_id) components."""
    if "-" in sense_id:
        parts = sense_id.split("-")
        if len(parts) == 2 and parts[0].startswith("L") and parts[1].startswith("S"):
            return parts[0], parts[1]
    elif sense_id.startswith("S"):
        return "", sense_id
    raise HTTPException(status_code=400, detail=f"Invalid sense ID format: {sense_id}")


QID_PATTERN = re.compile(r"^Q\d+$")


def _validate_qid(value: str, field_name: str) -> str:
    """Validate that a value is a valid QID format (Q followed by digits)."""
    if not value:
        raise HTTPException(
            status_code=400, detail=f"{field_name} is required and cannot be empty"
        )
    if not QID_PATTERN.match(value):
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be a valid QID format (Q followed by digits), got: {value}",
        )
    return value


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

    _validate_qid(request.language, "language")

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

    _validate_qid(request.lexical_category, "lexical_category")

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


@router.get("/entities/lexemes/{lexeme_id}/forms")
async def get_lexeme_forms(lexeme_id: str, req: Request):
    """Get all forms for a lexeme, sorted by numeric suffix."""
    from models.data.rest_api.v1.entitybase.response.lexemes import (
        FormsResponse,
        FormResponse,
        RepresentationData,
    )

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    forms_data = entity.entity_data.revision.get("forms", [])

    forms = []
    for form in forms_data:
        representations = {
            lang: RepresentationData(language=lang, value=data["value"])
            for lang, data in form.get("representations", {}).items()
        }
        forms.append(
            FormResponse(
                id=form["id"],
                representations=representations,
                grammaticalFeatures=form.get("grammatical_features", []),
                claims=form.get("claims", {}),
            )
        )

    forms.sort(key=lambda f: _extract_numeric_suffix(f.id))

    return FormsResponse(forms=forms)


@router.get("/entities/lexemes/{lexeme_id}/senses")
async def get_lexeme_senses(lexeme_id: str, req: Request):
    """Get all senses for a lexeme, sorted by numeric suffix."""
    from models.data.rest_api.v1.entitybase.response.lexemes import (
        SensesResponse,
        SenseResponse,
        RepresentationData,
    )

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    senses_data = entity.entity_data.revision.get("senses", [])

    senses = []
    for sense in senses_data:
        glosses = {
            lang: RepresentationData(language=lang, value=data["value"])
            for lang, data in sense.get("glosses", {}).items()
        }
        senses.append(
            SenseResponse(
                id=sense["id"], glosses=glosses, claims=sense.get("claims", {})
            )
        )

    senses.sort(key=lambda s: _extract_numeric_suffix(s.id))

    return SensesResponse(senses=senses)


@router.get("/entities/lexemes/forms/{form_id}")
async def get_form_by_id(form_id: str, req: Request):
    """Get form by ID."""
    lexeme_id, _ = _parse_form_id(form_id)
    if not lexeme_id:
        raise HTTPException(
            status_code=400, detail="Short format form ID not implemented"
        )

    from models.data.rest_api.v1.entitybase.response.lexemes import (
        FormResponse,
        RepresentationData,
    )

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    forms_data = entity.entity_data.revision.get("forms", [])

    for form in forms_data:
        if form["id"] == form_id:
            representations = {
                lang: RepresentationData(language=lang, value=data["value"])
                for lang, data in form.get("representations", {}).items()
            }
            return FormResponse(
                id=form_id,
                representations=representations,
                grammaticalFeatures=form.get("grammatical_features", []),
                claims=form.get("claims", {}),
            )

    raise HTTPException(status_code=404, detail=f"Form not found: {form_id}")


@router.get("/entities/lexemes/senses/{sense_id}")
async def get_sense_by_id(sense_id: str, req: Request):
    """Get sense by ID."""
    lexeme_id, _ = _parse_sense_id(sense_id)
    if not lexeme_id:
        raise HTTPException(
            status_code=400, detail="Short format sense ID not implemented"
        )

    from models.data.rest_api.v1.entitybase.response.lexemes import (
        SenseResponse,
        RepresentationData,
    )

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    senses_data = entity.entity_data.revision.get("senses", [])

    for sense in senses_data:
        if sense["id"] == sense_id:
            glosses = {
                lang: RepresentationData(language=lang, value=data["value"])
                for lang, data in sense.get("glosses", {}).items()
            }
            return SenseResponse(
                id=sense_id, glosses=glosses, claims=sense.get("claims", {})
            )

    raise HTTPException(status_code=404, detail=f"Sense not found: {sense_id}")


@router.put("/entities/lexemes/forms/{form_id}/representations/{langcode}")
async def update_form_representation(
    form_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update form representation for a language."""
    logger.debug(f"Updating form {form_id} representation for language {langcode}")

    if request.language != langcode:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({langcode})",
        )

    lexeme_id, _ = _parse_form_id(form_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)
    forms_data = current_entity.entity_data.revision.get("forms", [])

    form_found = False
    for form in forms_data:
        if form["id"] == form_id:
            if langcode not in form.get("representations", {}):
                raise HTTPException(
                    status_code=400,
                    detail=f"Language {langcode} does not exist in form representations",
                )
            form["representations"][langcode]["value"] = request.value
            form_found = True
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form not found: {form_id}")

    logger.debug(f"Updated form {form_id} representation in language {langcode}")

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
    "/entities/lexemes/forms/{form_id}/representations/{langcode}",
    response_model=EntityResponse,
)
async def delete_form_representation(
    form_id: str,
    langcode: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete form representation for a language."""
    logger.debug(f"Deleting form {form_id} representation for language {langcode}")

    lexeme_id, _ = _parse_form_id(form_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)
    forms_data = current_entity.entity_data.revision.get("forms", [])

    form_found = False
    for form in forms_data:
        if form["id"] == form_id:
            form_found = True
            if langcode not in form.get("representations", {}):
                raise HTTPException(
                    status_code=404,
                    detail=f"Language {langcode} not found in form representations",
                )
            del form["representations"][langcode]
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form not found: {form_id}")

    logger.debug(f"Deleted form {form_id} representation in language {langcode}")

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


@router.delete("/entities/lexemes/forms/{form_id}", response_model=EntityResponse)
async def delete_form(
    form_id: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete a form."""
    lexeme_id, _ = _parse_form_id(form_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)
    forms_data = current_entity.entity_data.revision.get("forms", [])

    original_len = len(forms_data)
    forms_data[:] = [f for f in forms_data if f["id"] != form_id]

    if len(forms_data) == original_len:
        raise HTTPException(status_code=404, detail=f"Form not found: {form_id}")

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
    "/entities/lexemes/senses/{sense_id}/glosses/{langcode}",
    response_model=EntityResponse,
)
async def delete_sense_gloss(
    sense_id: str,
    langcode: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete sense gloss for a language."""
    logger.debug(f"Deleting sense {sense_id} gloss for language {langcode}")

    lexeme_id, _ = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)
    senses_data = current_entity.entity_data.revision.get("senses", [])

    sense_found = False
    gloss_found = False
    for sense in senses_data:
        if sense["id"] == sense_id:
            sense_found = True
            if langcode in sense.get("glosses", {}):
                del sense["glosses"][langcode]
                gloss_found = True
            break

    if not sense_found:
        raise HTTPException(status_code=404, detail=f"Sense not found: {sense_id}")

    if not gloss_found:
        return current_entity

    logger.debug(f"Deleted sense {sense_id} gloss in language {langcode}")

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


@router.delete("/entities/lexemes/senses/{sense_id}", response_model=EntityResponse)
async def delete_sense(
    sense_id: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete a sense."""
    lexeme_id, _ = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)
    senses_data = current_entity.entity_data.revision.get("senses", [])

    original_len = len(senses_data)
    senses_data[:] = [s for s in senses_data if s["id"] != sense_id]

    if len(senses_data) == original_len:
        raise HTTPException(status_code=404, detail=f"Sense not found: {sense_id}")

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
