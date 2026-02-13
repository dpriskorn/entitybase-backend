"""Label endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
from models.data.rest_api.v1.entitybase.request.entity import TermUpdateContext
from models.data.rest_api.v1.entitybase.response import LabelResponse, EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/entities/{entity_id}/labels/{language_code}",
    response_model=LabelResponse,
)
async def get_entity_label(
    entity_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get entity label text for language."""
    logger.info(f"Getting label for entity {entity_id}, language {language_code}")
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(entity_id)

    labels_hashes = response.entity_data.revision.get("hashes", {}).get("labels", {})
    if language_code not in labels_hashes:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )

    hash_value = int(labels_hashes[language_code])
    label_text = state.s3_client.load_metadata("labels", hash_value)
    if label_text is None:
        raise HTTPException(
            status_code=404, detail=f"Label not found for hash {hash_value}"
        )
    return LabelResponse(value=str(label_text.data))


@router.put(
    "/entities/{entity_id}/labels/{language_code}", response_model=EntityResponse
)
async def update_entity_label(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update entity label for language."""
    logger.info(
        f"📝 LABEL UPDATE: Starting label update for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_label(
        entity_id,
        context,
        headers,
        validator,
    )

    return result


@router.delete(
    "/entities/{entity_id}/labels/{language_code}", response_model=EntityResponse
)
async def delete_entity_label(
    entity_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete entity label for language."""
    logger.info(
        f"🗑️ LABEL DELETE: Starting label deletion for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.delete_label(
        entity_id,
        language_code,
        headers,
        validator,
    )

    return result


@router.post(
    "/entities/{entity_id}/labels/{language_code}", response_model=EntityResponse
)
async def add_entity_label(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Add a new label to entity for language (alias for PUT)."""
    logger.info(
        f"📝 LABEL ADD: Starting label add for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_label(
        entity_id,
        context,
        headers,
        validator,
    )

    return result
