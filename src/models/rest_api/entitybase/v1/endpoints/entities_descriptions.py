"""Description endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
from models.data.rest_api.v1.entitybase.request.entity import TermUpdateContext
from models.data.rest_api.v1.entitybase.response import (
    DescriptionResponse,
    TermHashResponse,
    DeleteResponse,
)
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/entities/{entity_id}/descriptions/{language_code}",
    response_model=DescriptionResponse,
)
async def get_entity_description(
    entity_id: str, language_code: str, req: Request
) -> DescriptionResponse:
    """Get entity description text for language."""
    logger.info(f"Getting description for entity {entity_id}, language {language_code}")
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(entity_id)

    descriptions_hashes = response.entity_data.revision.get("hashes", {}).get(
        "descriptions", {}
    )
    if language_code not in descriptions_hashes:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )

    hash_value = int(descriptions_hashes[language_code])
    description_text = state.s3_client.load_metadata("descriptions", hash_value)
    if description_text is None:
        raise HTTPException(
            status_code=404, detail=f"Description not found for hash {hash_value}"
        )
    return DescriptionResponse(value=str(description_text.data))


@router.put(
    "/entities/{entity_id}/descriptions/{language_code}",
    response_model=TermHashResponse,
)
async def update_entity_description(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
    """Update entity description for language."""
    logger.info(
        f"📝 DESCRIPTION UPDATE: Starting description update for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    update_handler = EntityUpdateHandler(state=state)
    await update_handler.update_description(
        entity_id,
        context,
        headers,
        validator,
    )

    hash_value = MetadataExtractor.hash_string(request.value)
    return TermHashResponse(hash=hash_value)


@router.delete(
    "/entities/{entity_id}/descriptions/{language_code}", response_model=DeleteResponse
)
async def delete_entity_description(
    entity_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> DeleteResponse:
    """Delete entity description for language."""
    logger.info(
        f"🗑️ DESCRIPTION DELETE: Starting description deletion for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    await update_handler.delete_description(
        entity_id,
        language_code,
        headers,
        validator,
    )

    return DeleteResponse(success=True)


@router.post(
    "/entities/{entity_id}/descriptions/{language_code}",
    response_model=TermHashResponse,
)
async def add_entity_description(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
    """Add a new description to entity for language (alias for PUT)."""
    logger.info(
        f"📝 DESCRIPTION ADD: Starting description add for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    update_handler = EntityUpdateHandler(state=state)
    await update_handler.update_description(
        entity_id,
        context,
        headers,
        validator,
    )

    hash_value = MetadataExtractor.hash_string(request.value)
    return TermHashResponse(hash=hash_value)
