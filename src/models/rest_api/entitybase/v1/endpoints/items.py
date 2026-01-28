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
    logger.info(f"📝 LABEL UPDATE: Starting label update for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Extract label from request
    label_value = update_data.get("value")
    if label_value is None:
        logger.warning(f"📝 LABEL UPDATE: Missing 'value' field for item={item_id}")
        raise HTTPException(status_code=400, detail="Missing 'value' field")

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)
    logger.debug(f"📝 LABEL UPDATE: Retrieved current entity with {len(current_entity.entity_data)} fields")

    # Update label
    if "labels" not in current_entity.entity_data:
        current_entity.entity_data["labels"] = {}
    current_entity.entity_data["labels"][language_code] = {
        "language": language_code,
        "value": label_value,
    }
    logger.debug(f"📝 LABEL UPDATE: Updated label for {language_code}")

    # Filter to only valid EntityUpdateRequest fields
    valid_fields = {
        "id", "type", "labels", "descriptions", "claims", "aliases", "sitelinks",
        "is_mass_edit", "state", "edit_type", "is_not_autoconfirmed_user",
        "edit_summary", "user_id"
    }
    filtered_data = {k: v for k, v in current_entity.entity_data.items() if k in valid_fields}
    logger.info(f"📝 LABEL UPDATE: Filtered entity data from {len(current_entity.entity_data)} fields to {len(filtered_data)} valid fields")
    logger.debug(f"📝 LABEL UPDATE: Valid fields: {sorted(filtered_data.keys())}")

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    try:
        update_request = EntityUpdateRequest(
            type=entity_type, edit_summary=edit_summary, id=item_id, **filtered_data
        )
        logger.debug(f"📝 LABEL UPDATE: Created EntityUpdateRequest successfully")
    except Exception as e:
        logger.error(f"📝 LABEL UPDATE: Failed to create EntityUpdateRequest: {e}", exc_info=True)
        raise

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
    logger.info(f"🗑️ LABEL DELETE: Starting label deletion for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Check if label exists
    labels = current_entity.entity_data.get("labels", {})
    if language_code not in labels:
        # Idempotent - return current entity if label doesn't exist
        logger.info(f"🗑️ LABEL DELETE: Label for {language_code} does not exist, returning current entity")
        return current_entity

    # Remove label
    del current_entity.entity_data["labels"][language_code]
    logger.debug(f"🗑️ LABEL DELETE: Removed label for {language_code}")

    # Filter to only valid EntityUpdateRequest fields
    valid_fields = {
        "id", "type", "labels", "descriptions", "claims", "aliases", "sitelinks",
        "is_mass_edit", "state", "edit_type", "is_not_autoconfirmed_user",
        "edit_summary", "user_id"
    }
    filtered_data = {k: v for k, v in current_entity.entity_data.items() if k in valid_fields}
    logger.info(f"🗑️ LABEL DELETE: Filtered entity data from {len(current_entity.entity_data)} fields to {len(filtered_data)} valid fields")
    logger.debug(f"🗑️ LABEL DELETE: Valid fields: {sorted(filtered_data.keys())}")

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    try:
        update_request = EntityUpdateRequest(
            type=entity_type, edit_summary=edit_summary, id=item_id, **filtered_data
        )
        logger.debug(f"🗑️ LABEL DELETE: Created EntityUpdateRequest successfully")
    except Exception as e:
        logger.error(f"🗑️ LABEL DELETE: Failed to create EntityUpdateRequest: {e}", exc_info=True)
        raise

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
    logger.info(f"📝 DESCRIPTION UPDATE: Starting description update for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Extract description from Wikibase format
    description_value = update_data.get("description")
    if description_value is None:
        logger.warning(f"📝 DESCRIPTION UPDATE: Missing 'description' field for item={item_id}")
        raise HTTPException(status_code=400, detail="Missing 'description' field")

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)
    logger.debug(f"📝 DESCRIPTION UPDATE: Retrieved current entity with {len(current_entity.entity_data)} fields")

    # Update description
    if "descriptions" not in current_entity.entity_data:
        current_entity.entity_data["descriptions"] = {}
    current_entity.entity_data["descriptions"][language_code] = {
        "language": language_code,
        "value": description_value,
    }
    logger.debug(f"📝 DESCRIPTION UPDATE: Updated description for {language_code}")

    # Filter to only valid EntityUpdateRequest fields
    valid_fields = {
        "id", "type", "labels", "descriptions", "claims", "aliases", "sitelinks",
        "is_mass_edit", "state", "edit_type", "is_not_autoconfirmed_user",
        "edit_summary", "user_id"
    }
    filtered_data = {k: v for k, v in current_entity.entity_data.items() if k in valid_fields}
    logger.info(f"📝 DESCRIPTION UPDATE: Filtered entity data from {len(current_entity.entity_data)} fields to {len(filtered_data)} valid fields")
    logger.debug(f"📝 DESCRIPTION UPDATE: Valid fields: {sorted(filtered_data.keys())}")

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    try:
        update_request = EntityUpdateRequest(
            type=entity_type, edit_summary=edit_summary, id=item_id, **filtered_data
        )
        logger.debug(f"📝 DESCRIPTION UPDATE: Created EntityUpdateRequest successfully")
    except Exception as e:
        logger.error(f"📝 DESCRIPTION UPDATE: Failed to create EntityUpdateRequest: {e}", exc_info=True)
        raise

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
    logger.info(f"🗑️ DESCRIPTION DELETE: Starting description deletion for item={item_id}, language={language_code}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)

    # Check if description exists
    descriptions = current_entity.entity_data.get("descriptions", {})
    if language_code not in descriptions:
        # Idempotent - return current entity if description doesn't exist
        logger.info(f"🗑️ DESCRIPTION DELETE: Description for {language_code} does not exist, returning current entity")
        return current_entity

    # Remove description
    del current_entity.entity_data["descriptions"][language_code]
    logger.debug(f"🗑️ DESCRIPTION DELETE: Removed description for {language_code}")

    # Filter to only valid EntityUpdateRequest fields
    valid_fields = {
        "id", "type", "labels", "descriptions", "claims", "aliases", "sitelinks",
        "is_mass_edit", "state", "edit_type", "is_not_autoconfirmed_user",
        "edit_summary", "user_id"
    }
    filtered_data = {k: v for k, v in current_entity.entity_data.items() if k in valid_fields}
    logger.info(f"🗑️ DESCRIPTION DELETE: Filtered entity data from {len(current_entity.entity_data)} fields to {len(filtered_data)} valid fields")
    logger.debug(f"🗑️ DESCRIPTION DELETE: Valid fields: {sorted(filtered_data.keys())}")

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    try:
        update_request = EntityUpdateRequest(
            type=entity_type, edit_summary=edit_summary, id=item_id, **filtered_data
        )
        logger.debug(f"🗑️ DESCRIPTION DELETE: Created EntityUpdateRequest successfully")
    except Exception as e:
        logger.error(f"🗑️ DESCRIPTION DELETE: Failed to create EntityUpdateRequest: {e}", exc_info=True)
        raise

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
    logger.info(f"📝 ALIASES UPDATE: Starting aliases update for item={item_id}, language={language_code}")
    logger.debug(f"📝 ALIASES UPDATE: New aliases count: {len(aliases_data)}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(item_id)
    logger.debug(f"📝 ALIASES UPDATE: Retrieved current entity with {len(current_entity.entity_data)} fields")

    # Update aliases: expect list of strings
    if "aliases" not in current_entity.entity_data:
        current_entity.entity_data["aliases"] = {}
    # Convert to the internal format: list of dicts with "value"
    current_entity.entity_data["aliases"][language_code] = [
        {"value": alias} for alias in aliases_data
    ]
    logger.debug(f"📝 ALIASES UPDATE: Updated aliases for {language_code}")

    # Filter to only valid EntityUpdateRequest fields
    valid_fields = {
        "id", "type", "labels", "descriptions", "claims", "aliases", "sitelinks",
        "is_mass_edit", "state", "edit_type", "is_not_autoconfirmed_user",
        "edit_summary", "user_id"
    }
    filtered_data = {k: v for k, v in current_entity.entity_data.items() if k in valid_fields}
    logger.info(f"📝 ALIASES UPDATE: Filtered entity data from {len(current_entity.entity_data)} fields to {len(filtered_data)} valid fields")
    logger.debug(f"📝 ALIASES UPDATE: Valid fields: {sorted(filtered_data.keys())}")

    # Create new revision
    update_handler = EntityUpdateHandler(state=state)
    entity_type = current_entity.entity_data.get("type") or "item"
    try:
        update_request = EntityUpdateRequest(
            type=entity_type, edit_summary=edit_summary, id=item_id, **filtered_data
        )
        logger.debug(f"📝 ALIASES UPDATE: Created EntityUpdateRequest successfully")
    except Exception as e:
        logger.error(f"📝 ALIASES UPDATE: Failed to create EntityUpdateRequest: {e}", exc_info=True)
        raise

    return await update_handler.update_entity(
        item_id,
        update_request,
        validator,
    )
