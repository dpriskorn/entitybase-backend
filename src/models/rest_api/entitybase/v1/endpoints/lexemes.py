"""Lexeme endpoints for Entitybase v1 API."""

import logging
import re
from typing import Optional, cast

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
    LexemeUpdateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    FormRepresentationResponse,
    FormRepresentationsResponse,
    FormResponse,
    FormsResponse,
    LemmaResponse,
    LemmasResponse,
    SenseGlossResponse,
    SenseGlossesResponse,
    SenseResponse,
    SensesResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import (
    EntityUpdateHandler,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Sub-routers for representations and glosses
representations_router = APIRouter(prefix="/representations", tags=["lexemes"])
glosses_router = APIRouter(prefix="/glosses", tags=["lexemes"])

# Include sub-routers
router.include_router(representations_router)
router.include_router(glosses_router)


def _parse_form_id(form_id: str) -> tuple[str, str]:
    """Parse form ID and extract lexeme ID and form suffix.

    Args:
        form_id: Form ID like "L42-F1" or "F1"

    Returns:
        Tuple of (lexeme_id, form_suffix) like ("L42", "F1")

    Raises:
        HTTPException: If format is invalid
    """
    # Try full format L42-F1
    full_match = re.match(r"^(L\d+)-(F\d+)$", form_id)
    if full_match:
        return full_match.group(1), full_match.group(2)

    # Try short format F1
    short_match = re.match(r"^(F\d+)$", form_id)
    if short_match:
        return "", short_match.group(1)

    raise HTTPException(
        status_code=400, detail="Invalid form ID format. Use L42-F1 or F1"
    )


def _parse_sense_id(sense_id: str) -> tuple[str, str]:
    """Parse sense ID and extract lexeme ID and sense suffix.

    Args:
        sense_id: Sense ID like "L42-S1" or "S1"

    Returns:
        Tuple of (lexeme_id, sense_suffix) like ("L42", "S1")

    Raises:
        HTTPException: If format is invalid
    """
    # Try full format L42-S1
    full_match = re.match(r"^(L\d+)-(S\d+)$", sense_id)
    if full_match:
        return full_match.group(1), full_match.group(2)

    # Try short format S1
    short_match = re.match(r"^(S\d+)$", sense_id)
    if short_match:
        return "", short_match.group(1)

    raise HTTPException(
        status_code=400, detail="Invalid sense ID format. Use L42-S1 or S1"
    )


def _extract_numeric_suffix(suffix: str) -> int:
    """Extract numeric value from form/sense suffix like 'F1' -> 1."""
    return int(suffix[1:])


@router.get("/entities/lexemes/{lexeme_id}/forms", response_model=FormsResponse)
async def get_lexeme_forms(lexeme_id: str, req: Request) -> FormsResponse:
    """List all forms for a lexeme, sorted by numeric suffix."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    forms_data = entity.entity_data.revision.get("forms", [])

    forms = []
    for form in forms_data:
        forms.append(FormResponse(**form))

    forms.sort(key=lambda f: _extract_numeric_suffix(f.id.split("-")[-1]))
    return FormsResponse(forms=forms)


@router.get("/entities/lexemes/{lexeme_id}/senses", response_model=SensesResponse)
async def get_lexeme_senses(lexeme_id: str, req: Request) -> SensesResponse:
    """List all senses for a lexeme, sorted by numeric suffix."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity = handler.get_entity(lexeme_id)
    senses_data = entity.entity_data.revision.get("senses", [])

    senses = []
    for sense in senses_data:
        senses.append(SenseResponse(**sense))

    senses.sort(key=lambda s: _extract_numeric_suffix(s.id.split("-")[-1]))
    return SensesResponse(senses=senses)


@router.get("/entities/lexemes/forms/{form_id}", response_model=FormResponse)
async def get_form_by_id(form_id: str, req: Request) -> FormResponse:
    """Get single form by ID (accepts L42-F1 or F1 format)."""
    lexeme_id, form_suffix = _parse_form_id(form_id)

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)

    if lexeme_id:
        entity = handler.get_entity(lexeme_id)
        full_form_id = form_id
    else:
        # For short format F1, need to find the lexeme containing this form
        # For now, we'll require full format or add a search later
        raise HTTPException(
            status_code=400,
            detail="Short format F1 not yet supported - use full L42-F1 format",
        )

    forms_data = entity.entity_data.revision.get("forms", [])
    for form in forms_data:
        if form["id"] == full_form_id:
            return FormResponse(**form)

    raise HTTPException(status_code=404, detail=f"Form {full_form_id} not found")


@router.get("/entities/lexemes/senses/{sense_id}", response_model=SenseResponse)
async def get_sense_by_id(sense_id: str, req: Request) -> SenseResponse:
    """Get single sense by ID (accepts L42-S1 or S1 format)."""
    lexeme_id, sense_suffix = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)

    if lexeme_id:
        entity = handler.get_entity(lexeme_id)
        full_sense_id = sense_id
    else:
        # For short format S1, need to find the lexeme containing this sense
        raise HTTPException(
            status_code=400,
            detail="Short format S1 not yet supported - use full L42-S1 format",
        )

    senses_data = entity.entity_data.revision.get("senses", [])
    for sense in senses_data:
        if sense["id"] == full_sense_id:
            return SenseResponse(**sense)

    raise HTTPException(status_code=404, detail=f"Sense {full_sense_id} not found")


@router.get(
    "/entities/lexemes/forms/{form_id}/representation",
    response_model=FormRepresentationsResponse,
)
async def get_form_representations(
    form_id: str, req: Request
) -> FormRepresentationsResponse:
    """Get all representations for a form."""
    form = await get_form_by_id(form_id, req)
    return FormRepresentationsResponse(representations=form.representations)


@router.get(
    "/entities/lexemes/forms/{form_id}/representation/{langcode}",
    response_model=FormRepresentationResponse,
)
async def get_form_representation(
    form_id: str, langcode: str, req: Request
) -> FormRepresentationResponse:
    """Get representation for a form in specific language."""
    form = await get_form_by_id(form_id, req)
    representation = form.representations.get(langcode)
    if not representation:
        raise HTTPException(
            status_code=404, detail=f"Representation not found for language {langcode}"
        )
    return FormRepresentationResponse(value=representation.value)


@router.get(
    "/entities/lexemes/senses/{sense_id}/glosses", response_model=SenseGlossesResponse
)
async def get_sense_glosses(sense_id: str, req: Request) -> SenseGlossesResponse:
    """Get all glosses for a sense."""
    sense = await get_sense_by_id(sense_id, req)
    return SenseGlossesResponse(glosses=sense.glosses)


@router.get(
    "/entities/lexemes/senses/{sense_id}/glosses/{langcode}",
    response_model=SenseGlossResponse,
)
async def get_sense_gloss(
    sense_id: str, langcode: str, req: Request
) -> SenseGlossResponse:
    """Get gloss for a sense in specific language."""
    sense = await get_sense_by_id(sense_id, req)
    gloss = sense.glosses.get(langcode)
    if not gloss:
        raise HTTPException(
            status_code=404, detail=f"Gloss not found for language {langcode}"
        )
    return SenseGlossResponse(value=gloss.value)


@router.put(
    "/entities/lexemes/forms/{form_id}/representation/{langcode}",
    response_model=EntityResponse,
)
async def update_form_representation(
    form_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update form representation for language."""
    logger.debug(f"Updating representation for form {form_id}, language {langcode}")
    lexeme_id, form_suffix = _parse_form_id(form_id)

    if request.language != langcode:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({langcode})",
        )

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current lexeme entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    # Find the form in the entity data
    forms_data = current_entity.entity_data.revision.get("forms", [])
    form_found = False
    for form in forms_data:
        if form["id"] == form_id:
            form_found = True
            representations = form.get("representations", {})
            if langcode not in representations:
                raise HTTPException(
                    status_code=404,
                    detail=f"Representation not found for language {langcode}",
                )

            # Update the representation value
            form["representations"][langcode] = {
                "language": langcode,
                "value": request.value,
            }
            logger.debug(
                f"Updated representation value for form {form_id} in language {langcode}"
            )
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

    # Create new revision
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
    "/entities/lexemes/senses/{sense_id}/glosses/{langcode}",
    response_model=EntityResponse,
)
async def update_sense_gloss(
    sense_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update sense gloss for language."""
    logger.debug(f"Updating gloss for sense {sense_id}, language {langcode}")
    lexeme_id, sense_suffix = _parse_sense_id(sense_id)

    if request.language != langcode:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({langcode})",
        )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current lexeme entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    # Find the sense in the entity data
    senses_data = current_entity.entity_data.revision.get("senses", [])
    sense_found = False
    for sense in senses_data:
        if sense["id"] == sense_id:
            sense_found = True
            glosses = sense.get("glosses", {})
            if langcode not in glosses:
                raise HTTPException(
                    status_code=404, detail=f"Gloss not found for language {langcode}"
                )

            # Update the gloss value
            sense["glosses"][langcode] = {"language": langcode, "value": request.value}
            logger.debug(
                f"Updated gloss value for sense {sense_id} in language {langcode}"
            )
            break

    if not sense_found:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

    # Create new revision
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
    """Delete a form by ID."""
    logger.debug(f"Deleting form {form_id}")
    lexeme_id, form_suffix = _parse_form_id(form_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current lexeme entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    # Find and remove the form from entity data
    forms_data = current_entity.entity_data.revision.get("forms", [])
    form_index = -1
    for i, form in enumerate(forms_data):
        if form["id"] == form_id:
            form_index = i
            break

    if form_index == -1:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

    # Remove the form from the list
    del forms_data[form_index]
    logger.debug(f"Removed form {form_id} from lexeme {lexeme_id}")

    # Create new revision
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
    """Delete a sense by ID."""
    logger.debug(f"Deleting sense {sense_id}")
    lexeme_id, sense_suffix = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current lexeme entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    # Find and remove the sense from entity data
    senses_data = current_entity.entity_data.revision.get("senses", [])
    sense_index = -1
    for i, sense in enumerate(senses_data):
        if sense["id"] == sense_id:
            sense_index = i
            break

    if sense_index == -1:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

    # Remove the sense from the list
    del senses_data[sense_index]
    logger.debug(f"Removed sense {sense_id} from lexeme {lexeme_id}")

    # Create new revision
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


@representations_router.get("/{hashes}")
async def get_representations(req: Request, hashes: str) -> list[Optional[str]]:
    """Fetch form representations by hash(es).

    Supports single hash (e.g., /representations/123) or comma-separated batch
    (e.g., /representations/123,456,789).

    Returns array of representation strings in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = [h.strip() for h in hashes.split(",") if h.strip()]
    if not hash_list:
        raise HTTPException(status_code=400, detail="No hashes provided")

    if len(hash_list) > 100:
        raise HTTPException(status_code=400, detail="Too many hashes (max 100)")

    try:
        # Convert to int
        rapidhashes = [int(h) for h in hash_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hash format")

    try:
        result = state.s3_client.load_form_representations_batch(rapidhashes)
        return cast(list[str | None], result)
    except Exception as e:
        logger.error(f"Failed to load representations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@glosses_router.get("/{hashes}")
async def get_glosses(req: Request, hashes: str) -> list[Optional[str]]:
    """Fetch sense glosses by hash(es).

    Supports single hash (e.g., /glosses/123) or comma-separated batch
    (e.g., /glosses/123,456,789).

    Returns array of gloss strings in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = [h.strip() for h in hashes.split(",") if h.strip()]
    if not hash_list:
        raise HTTPException(status_code=400, detail="No hashes provided")

    if len(hash_list) > 100:
        raise HTTPException(status_code=400, detail="Too many hashes (max 100)")

    try:
        # Convert to int
        rapidhashes = [int(h) for h in hash_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hash format")

    try:
        result = state.s3_client.load_sense_glosses_batch(rapidhashes)
        return cast(list[str | None], result)
    except Exception as e:
        logger.error(f"Failed to load glosses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/entities/lexemes/forms/{form_id}/representation/{langcode}",
    response_model=EntityResponse,
)
async def delete_form_representation(
    form_id: str,
    langcode: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete form representation for language."""
    logger.debug(f"Deleting representation for form {form_id}, language {langcode}")
    lexeme_id, form_suffix = _parse_form_id(form_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current lexeme entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    # Find the form in the entity data
    forms_data = current_entity.entity_data.revision.get("forms", [])
    form_found = False
    for form in forms_data:
        if form["id"] == form_id:
            form_found = True
            representations = form.get("representations", {})
            if langcode not in representations:
                raise HTTPException(
                    status_code=404,
                    detail=f"Representation not found for language {langcode}",
                )

            # Delete the representation
            del form["representations"][langcode]
            logger.debug(
                f"Deleted representation for form {form_id} in language {langcode}"
            )
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(
        type="lexeme", **current_entity.entity_data.revision
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
    """Delete sense gloss for language."""
    logger.debug(f"Deleting gloss for sense {sense_id}, language {langcode}")
    lexeme_id, sense_suffix = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current lexeme entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    # Find the sense in the entity data
    senses_data = current_entity.entity_data.revision.get("senses", [])
    sense_found = False
    for sense in senses_data:
        if sense["id"] == sense_id:
            sense_found = True
            glosses = sense.get("glosses", {})
            if langcode not in glosses:
                # Idempotent: return current entity if gloss doesn't exist
                return current_entity

            # Delete the gloss
            del sense["glosses"][langcode]
            logger.debug(f"Deleted gloss for sense {sense_id} in language {langcode}")
            break

    if not sense_found:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

    # Create new revision
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
