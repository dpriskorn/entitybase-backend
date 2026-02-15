"""Form endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request import (
    AddStatementRequest,
    FormCreateRequest,
    LexemeUpdateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    DeleteResponse,
    EntityResponse,
    FormRepresentationResponse,
    FormRepresentationsResponse,
    FormResponse,
    FormsResponse,
    TermHashResponse,
)
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
    _extract_numeric_suffix,
    _parse_form_id,
)

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType

logger = logging.getLogger(__name__)

router = APIRouter()


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


@router.post("/entities/lexemes/{lexeme_id}/forms", response_model=EntityResponse)
async def create_lexeme_form(
    lexeme_id: str,
    request: FormCreateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Create a new form for a lexeme."""
    logger.debug(f"Creating form for lexeme {lexeme_id}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    forms_data = current_entity.entity_data.revision.get("forms", [])

    max_form_num = 0
    for form in forms_data:
        form_id = form.get("id", "")
        if "-" in form_id:
            suffix = form_id.split("-")[-1]
            if suffix.startswith("F"):
                try:
                    num = int(suffix[1:])
                    max_form_num = max(max_form_num, num)
                except ValueError:
                    pass

    new_form_num = max_form_num + 1
    new_form_id = f"{lexeme_id}-F{new_form_num}"

    new_form = {
        "id": new_form_id,
        "representations": request.representations,
        "grammaticalFeatures": request.grammatical_features,
        "claims": request.claims,
    }

    forms_data.append(new_form)
    logger.debug(f"Created form {new_form_id} for lexeme {lexeme_id}")

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


@router.get("/entities/lexemes/forms/{form_id}", response_model=FormResponse)
async def get_form_by_id(form_id: str, req: Request) -> FormResponse:
    """Get single form by ID (accepts L42-F1 or F1 format)."""
    lexeme_id, _ = _parse_form_id(form_id)

    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)

    if lexeme_id:
        entity = handler.get_entity(lexeme_id)
        full_form_id = form_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Short format F1 not yet supported - use full L42-F1 format",
        )

    forms_data = entity.entity_data.revision.get("forms", [])
    for form in forms_data:
        if form["id"] == full_form_id:
            return FormResponse(**form)

    raise HTTPException(status_code=404, detail=f"Form {full_form_id} not found")


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


@router.post(
    "/entities/lexemes/forms/{form_id}/representation/{langcode}",
    response_model=TermHashResponse,
)
async def add_form_representation(
    form_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
    """Add a new form representation for language."""
    logger.debug(f"Adding representation for form {form_id}, language {langcode}")
    lexeme_id, _ = _parse_form_id(form_id)

    if request.language != langcode:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({langcode})",
        )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    forms_data = current_entity.entity_data.revision.get("forms", [])
    form_found = False
    for form in forms_data:
        if form["id"] == form_id:
            form_found = True
            representations = form.get("representations", {})
            if langcode in representations:
                raise HTTPException(
                    status_code=409,
                    detail=f"Representation already exists for language {langcode}. Use PUT to update.",
                )

            form["representations"][langcode] = {
                "language": langcode,
                "value": request.value,
            }
            logger.debug(
                f"Added representation for form {form_id} in language {langcode}"
            )
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

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
    "/entities/lexemes/forms/{form_id}/representation/{langcode}",
    response_model=TermHashResponse,
)
async def update_form_representation(
    form_id: str,
    langcode: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
    """Update form representation for language."""
    logger.debug(f"Updating representation for form {form_id}, language {langcode}")
    lexeme_id, _ = _parse_form_id(form_id)

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

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

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


@router.delete("/entities/lexemes/forms/{form_id}", response_model=EntityResponse)
async def delete_form(
    form_id: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete a form by ID."""
    logger.debug(f"Deleting form {form_id}")
    lexeme_id, _ = _parse_form_id(form_id)

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(lexeme_id)

    forms_data = current_entity.entity_data.revision.get("forms", [])
    form_index = -1
    for i, form in enumerate(forms_data):
        if form["id"] == form_id:
            form_index = i
            break

    if form_index == -1:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

    del forms_data[form_index]
    logger.debug(f"Removed form {form_id} from lexeme {lexeme_id}")

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
    "/entities/lexemes/forms/{form_id}/representation/{langcode}",
    response_model=DeleteResponse,
)
async def delete_form_representation(
    form_id: str,
    langcode: str,
    req: Request,
    headers: EditHeadersType,
) -> DeleteResponse:
    """Delete form representation for language."""
    logger.debug(f"Deleting representation for form {form_id}, language {langcode}")
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
            representations = form.get("representations", {})
            if langcode not in representations:
                raise HTTPException(
                    status_code=404,
                    detail=f"Representation not found for language {langcode}",
                )

            del form["representations"][langcode]
            logger.debug(
                f"Deleted representation for form {form_id} in language {langcode}"
            )
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

    update_handler = EntityUpdateHandler(state=state)
    update_request = LexemeUpdateRequest(
        type="lexeme", **current_entity.entity_data.revision
    )

    await update_handler.update_lexeme(
        lexeme_id,
        update_request,
        edit_headers=headers,
        validator=validator,
    )

    return DeleteResponse(success=True)


@router.post(
    "/entities/lexemes/forms/{form_id}/statements",
    response_model=EntityResponse,
)
async def add_form_statement(
    form_id: str,
    request: AddStatementRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Add a statement to a form."""
    logger.debug(f"Adding statement to form {form_id}")
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
            if "claims" not in form:
                form["claims"] = {}
            claim = request.claim
            property_id = claim.get("property", {}).get("id") or claim.get(
                "mainsnak", {}
            ).get("property")
            if not property_id:
                raise HTTPException(
                    status_code=400,
                    detail="Statement must have a property ID",
                )
            if property_id not in form["claims"]:
                form["claims"][property_id] = []
            form["claims"][property_id].append(claim)
            logger.debug(f"Added statement to form {form_id}")
            break

    if not form_found:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

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
