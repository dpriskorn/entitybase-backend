"""Item creation endpoints for Entitybase v1 API."""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.handlers.entity.item import ItemCreateHandler
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.request.entity import EntityCreateRequest, EntityUpdateRequest
from models.rest_api.entitybase.response import (
    EntityResponse,
)
from models.rest_api.entitybase.response.misc import DescriptionResponse, LabelResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/items", response_model=EntityResponse)
async def create_item(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new item entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = ItemCreateHandler(enumeration_service)
    return await handler.create_entity(
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )




@router.get(
    "/entities/items/{item_id}/labels/{language_code}", response_model=LabelResponse
)
async def get_item_label(
    item_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get item label for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(item_id, clients.vitess, clients.s3)
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
    item_id: str, language_code: str, update_data: Dict[str, Any], req: Request
) -> EntityResponse:
    """Update item label for language."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Extract label from request
    label_value = update_data.get("value")
    if label_value is None:
        raise HTTPException(status_code=400, detail="Missing 'value' field")

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Update label
    if "labels" not in current_entity.entity_data:
        current_entity.entity_data["labels"] = {}
    current_entity.entity_data["labels"][language_code] = {
        "language": language_code,
        "value": label_value,
    }

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    return await update_handler.update_entity(
        item_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.delete(
    "/entities/items/{item_id}/labels/{language_code}", response_model=EntityResponse
)
async def delete_item_label(
    item_id: str, language_code: str, req: Request
) -> EntityResponse:
    """Delete item label for language."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Check if label exists
    labels = current_entity.entity_data.get("labels", {})
    if language_code not in labels:
        # Idempotent - return current entity if label doesn't exist
        return current_entity

    # Remove label
    del current_entity.entity_data["labels"][language_code]

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    return await update_handler.update_entity(
        item_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
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
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(item_id, clients.vitess, clients.s3)
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
    item_id: str, language_code: str, update_data: Dict[str, Any], req: Request
) -> EntityResponse:
    """Update item description for language."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Extract description from Wikibase format
    description_value = update_data.get("description")
    if description_value is None:
        raise HTTPException(status_code=400, detail="Missing 'description' field")

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Update description
    if "descriptions" not in current_entity.entity_data:
        current_entity.entity_data["descriptions"] = {}
    current_entity.entity_data["descriptions"][language_code] = {
        "language": language_code,
        "value": description_value,
    }

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    return await update_handler.update_entity(
        item_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.delete(
    "/entities/items/{item_id}/descriptions/{language_code}",
    response_model=EntityResponse,
)
async def delete_item_description(
    item_id: str, language_code: str, req: Request
) -> EntityResponse:
    """Delete item description for language."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Check if description exists
    descriptions = current_entity.entity_data.get("descriptions", {})
    if language_code not in descriptions:
        # Idempotent - return current entity if description doesn't exist
        return current_entity

    # Remove description
    del current_entity.entity_data["descriptions"][language_code]

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    return await update_handler.update_entity(
        item_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.get(
    "/entities/items/{item_id}/aliases/{language_code}", response_model=List[str]
)
async def get_item_aliases_for_language(
    item_id: str, language_code: str, req: Request
) -> list[str]:
    """Get item aliases for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(item_id, clients.vitess, clients.s3)
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    return [alias["value"] for alias in aliases[language_code]]


@router.patch(
    "/entities/items/{item_id}/aliases/{language_code}", response_model=EntityResponse
)
async def patch_item_aliases_for_language(
    item_id: str, language_code: str, patch_data: Dict[str, Any], req: Request
) -> EntityResponse:
    """Patch item aliases for language using JSON Patch."""
    logger.debug(f"Patching aliases for item {item_id}, language {language_code}")
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Get current aliases for the language
    current_aliases = current_entity.entity_data.get("aliases", {}).get(
        language_code, []
    )

    # Apply JSON Patch operations
    patches = patch_data.get("patch", [])
    updated_aliases = current_aliases.copy()

    for patch_op in patches:
        op = patch_op.get("op")
        path = patch_op.get("path")
        value = patch_op.get("value")

        if op == "add":
            if path == "/-":  # Append to end
                updated_aliases.append(value)
            elif path.startswith("/") and path[1:].isdigit():
                index = int(path[1:])
                updated_aliases.insert(index, value)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported path: {path}")
        elif op == "remove":
            if path.startswith("/") and path[1:].isdigit():
                index = int(path[1:])
                if 0 <= index < len(updated_aliases):
                    updated_aliases.pop(index)
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid index: {index}"
                    )
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported path: {path}")
        elif op == "replace":
            if path.startswith("/") and path[1:].isdigit():
                index = int(path[1:])
                if 0 <= index < len(updated_aliases):
                    updated_aliases[index] = value
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid index: {index}"
                    )
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported path: {path}")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {op}")

    # Update entity data
    if "aliases" not in current_entity.entity_data:
        current_entity.entity_data["aliases"] = {}
    current_entity.entity_data["aliases"][language_code] = updated_aliases

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    return await update_handler.update_entity(
        item_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )
