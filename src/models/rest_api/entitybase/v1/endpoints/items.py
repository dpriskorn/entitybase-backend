"""Item creation endpoints for Entitybase v1 API."""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Header, HTTPException, Request

from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
    EntityUpdateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
)
from models.data.rest_api.v1.entitybase.response import (
    DescriptionResponse,
    LabelResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/items", response_model=EntityResponse)
async def create_item(request: EntityCreateRequest, req: Request) -> EntityResponse:
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

        result = await handler.create_entity(request, validator)
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
    labels = response.data.get("labels", {})
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
    update_data: Dict[str, Any],
    req: Request,
    edit_summary: str = Header(..., alias="X-Edit-Summary", min_length=1, max_length=200),
) -> EntityResponse:
    """Update item label for language."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Extract label from request
    label_value = update_data.get("value")
    if label_value is None:
        raise HTTPException(status_code=400, detail="Missing 'value' field")

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Update label
    if "labels" not in current_entity.entity_data:
        current_entity.entity_data["labels"] = {}
    current_entity.entity_data["labels"][language_code] = {
        "language": language_code,
        "value": label_value,
    }

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type, edit_summary=edit_summary, **current_entity.entity_data
    )

    return await update_handler.update_entity(
        item_id,
        update_request,
        validator,
    )


@router.delete(
    "/entities/items/{item_id}/labels/{language_code}", response_model=EntityResponse
)
async def delete_item_label(
    item_id: str,
    language_code: str,
    req: Request,
    edit_summary: str = Header(..., alias="X-Edit-Summary", min_length=1, max_length=200),
) -> EntityResponse:
    """Delete item label for language."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Check if label exists
    labels = current_entity.entity_data.get("labels", {})
    if language_code not in labels:
        # Idempotent - return current entity if label doesn't exist
        return current_entity

    # Remove label
    del current_entity.entity_data["labels"][language_code]

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type, edit_summary=edit_summary, **current_entity.entity_data
    )

    return await update_handler.update_entity(
        item_id,
        update_request,
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
    descriptions = response.data.get("descriptions", {})
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
    update_data: Dict[str, Any],
    req: Request,
    edit_summary: str = Header(..., alias="X-Edit-Summary", min_length=1, max_length=200),
) -> EntityResponse:
    """Update item description for language."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Extract description from Wikibase format
    description_value = update_data.get("description")
    if description_value is None:
        raise HTTPException(status_code=400, detail="Missing 'description' field")

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Update description
    if "descriptions" not in current_entity.entity_data:
        current_entity.entity_data["descriptions"] = {}
    current_entity.entity_data["descriptions"][language_code] = {
        "language": language_code,
        "value": description_value,
    }

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type, edit_summary=edit_summary, **current_entity.entity_data
    )

    return await update_handler.update_entity(
        item_id,
        update_request,
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
    edit_summary: str = Header(..., alias="X-Edit-Summary", min_length=1, max_length=200),
) -> EntityResponse:
    """Delete item description for language."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Check if description exists
    descriptions = current_entity.entity_data.get("descriptions", {})
    if language_code not in descriptions:
        # Idempotent - return current entity if description doesn't exist
        return current_entity

    # Remove description
    del current_entity.entity_data["descriptions"][language_code]

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type, edit_summary=edit_summary, **current_entity.entity_data
    )

    return await update_handler.update_entity(
        item_id,
        update_request,
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
    aliases = response.data.get("aliases", {})
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
    edit_summary: str = Header(..., alias="X-Edit-Summary", min_length=1, max_length=200),
) -> EntityResponse:
    """Update item aliases for language."""
    logger.debug(f"Updating aliases for item {item_id}, language {language_code}")
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Update aliases: expect list of strings
    if "aliases" not in current_entity.entity_data:
        current_entity.entity_data["aliases"] = {}
    # Convert to the internal format: list of dicts with "value"
    current_entity.entity_data["aliases"][language_code] = [
        {"value": alias} for alias in aliases_data
    ]

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type, edit_summary=edit_summary, **current_entity.entity_data
    )

    return await update_handler.update_entity(
        item_id,
        update_request,
        validator,
    )
