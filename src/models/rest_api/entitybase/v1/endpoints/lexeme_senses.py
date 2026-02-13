"""Sense endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request import (
    AddStatementRequest,
    LexemeUpdateRequest,
    SenseCreateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    SenseGlossResponse,
    SenseGlossesResponse,
    SenseResponse,
    SensesResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
    _extract_numeric_suffix,
    _parse_sense_id,
)

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType

logger = logging.getLogger(__name__)

router = APIRouter()


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


@router.post("/entities/lexemes/{lexeme_id}/senses", response_model=EntityResponse)
async def create_lexeme_sense(
    lexeme_id: str,
    request: SenseCreateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Create a new sense for a lexeme."""
    logger.debug(f"Creating sense for lexeme {lexeme_id}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    senses_data = current_entity.entity_data.revision.get("senses", [])

    max_sense_num = 0
    for sense in senses_data:
        sense_id = sense.get("id", "")
        if "-" in sense_id:
            suffix = sense_id.split("-")[-1]
            if suffix.startswith("S"):
                try:
                    num = int(suffix[1:])
                    max_sense_num = max(max_sense_num, num)
                except ValueError:
                    pass

    new_sense_num = max_sense_num + 1
    new_sense_id = f"{lexeme_id}-S{new_sense_num}"

    new_sense = {
        "id": new_sense_id,
        "glosses": request.glosses,
        "claims": request.claims,
    }

    senses_data.append(new_sense)
    logger.debug(f"Created sense {new_sense_id} for lexeme {lexeme_id}")

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

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

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

            sense["glosses"][langcode] = {"language": langcode, "value": request.value}
            logger.debug(
                f"Updated gloss value for sense {sense_id} in language {langcode}"
            )
            break

    if not sense_found:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

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

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    senses_data = current_entity.entity_data.revision.get("senses", [])
    sense_index = -1
    for i, sense in enumerate(senses_data):
        if sense["id"] == sense_id:
            sense_index = i
            break

    if sense_index == -1:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

    del senses_data[sense_index]
    logger.debug(f"Removed sense {sense_id} from lexeme {lexeme_id}")

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
    """Delete sense gloss for language."""
    logger.debug(f"Deleting gloss for sense {sense_id}, language {langcode}")
    lexeme_id, sense_suffix = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    senses_data = current_entity.entity_data.revision.get("senses", [])
    sense_found = False
    for sense in senses_data:
        if sense["id"] == sense_id:
            sense_found = True
            glosses = sense.get("glosses", {})
            if langcode not in glosses:
                return current_entity

            del sense["glosses"][langcode]
            logger.debug(f"Deleted gloss for sense {sense_id} in language {langcode}")
            break

    if not sense_found:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

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


@router.post(
    "/entities/lexemes/senses/{sense_id}/statements",
    response_model=EntityResponse,
)
async def add_sense_statement(
    sense_id: str,
    request: AddStatementRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Add a statement to a sense."""
    logger.debug(f"Adding statement to sense {sense_id}")
    lexeme_id, sense_suffix = _parse_sense_id(sense_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    senses_data = current_entity.entity_data.revision.get("senses", [])
    sense_found = False
    for sense in senses_data:
        if sense["id"] == sense_id:
            sense_found = True
            if "claims" not in sense:
                sense["claims"] = {}
            claim = request.claim
            property_id = claim.get("property", {}).get("id") or claim.get(
                "mainsnak", {}
            ).get("property")
            if not property_id:
                raise HTTPException(
                    status_code=400,
                    detail="Statement must have a property ID",
                )
            if property_id not in sense["claims"]:
                sense["claims"][property_id] = []
            sense["claims"][property_id].append(claim)
            logger.debug(f"Added statement to sense {sense_id}")
            break

    if not sense_found:
        raise HTTPException(status_code=404, detail=f"Sense {sense_id} not found")

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
