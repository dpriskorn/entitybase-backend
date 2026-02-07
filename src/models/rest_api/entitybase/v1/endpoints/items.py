"""Item creation endpoints for Entitybase v1 API."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.request.entity import TermUpdateContext
from models.data.rest_api.v1.entitybase.response import (
    DescriptionResponse,
    LabelResponse,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/items", response_model=EntityResponse)
async def create_item(
    request: EntityCreateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Create a new item entity."""
    logger.info(f"🔍 ENDPOINT: Received create request for {request.id or 'auto-assign'}")
    logger.debug(f"🔍 ENDPOINT: Request data: {request.model_dump()}")

    try:
        state = req.app.state.state_handler
        assert isinstance(state, StateHandler)
        validator = req.app.state.state_handler.validator
        enumeration_service = req.app.state.state_handler.enumeration_service

        logger.debug(f"🔍 ENDPOINT: Services available - state: {state is not None}, validator: {validator is not None}, enum_svc: {enumeration_service is not None}")

        handler = ItemCreateHandler(state=state, enumeration_service=enumeration_service)
        logger.info("🔍 ENDPOINT: Handler created, calling create_entity")

        result = await handler.create_entity(request, edit_headers=headers, validator=validator)
        logger.info(f"🔍 ENDPOINT: Entity creation successful: {result.id}")
        return result

    except Exception as e:
        logger.error(f"🔍 ENDPOINT: Create item failed: {e}", exc_info=True)
        raise


@router.get(
    "/entities/items/{item_id}/labels/{language_code}", response_model=LabelResponse
)
async def get_item_label(
    item_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get item label for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(item_id)
    labels = response.data.revision.get("labels", {})
    if language_code not in labels:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    return LabelResponse(value=labels[language_code])


@router.put(
    "/entities/items/{item_id}/labels/{language_code}", response_model=EntityResponse
)
async def update_item_label(
    item_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update item label for language."""
    logger.info(f"📝 LABEL UPDATE: Starting label update for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    # Update label using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    return await update_handler.update_label(
        item_id,
        context,
        headers,
        validator,
    )


@router.delete(
    "/entities/items/{item_id}/labels/{language_code}", response_model=EntityResponse
)
async def delete_item_label(
    item_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete item label for language."""
    logger.info(f"🗑️ LABEL DELETE: Starting label deletion for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Delete label using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    return await update_handler.delete_label(
        item_id,
        language_code,
        headers,
        validator,
    )


@router.get(
    "/entities/items/{item_id}/descriptions/{language_code}",
    response_model=DescriptionResponse,
)
async def get_item_description(
    item_id: str, language_code: str, req: Request
) -> DescriptionResponse:
    """Get item description for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(item_id)
    descriptions = response.data.revision.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )
    return DescriptionResponse(value=descriptions[language_code])


@router.put(
    "/entities/items/{item_id}/descriptions/{language_code}",
    response_model=EntityResponse,
)
async def update_item_description(
    item_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update item description for language."""
    logger.info(f"📝 DESCRIPTION UPDATE: Starting description update for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    # Update description using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    return await update_handler.update_description(
        item_id,
        context,
        headers,
        validator,
    )


@router.delete(
    "/entities/items/{item_id}/descriptions/{language_code}",
    response_model=EntityResponse,
)
async def delete_item_description(
    item_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete item description for language."""
    logger.info(f"🗑️ DESCRIPTION DELETE: Starting description deletion for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Delete description using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    return await update_handler.delete_description(
        item_id,
        language_code,
        headers,
        validator,
    )


@router.get(
    "/entities/items/{item_id}/aliases/{language_code}", response_model=List[str]
)
async def get_item_aliases_for_language(
    item_id: str, language_code: str, req: Request
) -> list[str]:
    """Get item aliases for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(item_id)
    aliases = response.data.revision.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    return [alias["value"] for alias in aliases[language_code]]


@router.put(
    "/entities/items/{item_id}/aliases/{language_code}", response_model=EntityResponse
)
async def put_item_aliases_for_language(
    item_id: str,
    language_code: str,
    aliases_data: List[str],
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update item aliases for language."""
    logger.info(f"📝 ALIASES UPDATE: Starting aliases update for item={item_id}, language={language_code}")
    logger.debug(f"📝 ALIASES UPDATE: New aliases count: {len(aliases_data)}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Update aliases using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    return await update_handler.update_aliases(
        item_id,
        language_code,
        aliases_data,
        headers,
        validator,
    )
