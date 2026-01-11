from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
import json

from models.rest_api.api.entity import (
    EntityCreateRequest,
    EntityResponse,
    EntityUpdateRequest,
)
from models.rest_api.request.entity import EntityJsonImportRequest
from models.rest_api.response.entity import EntityJsonImportResponse
from ...handlers.entity.item import ItemCreateHandler
from ...handlers.entity.items.update import ItemUpdateHandler
from ...handlers.entity.property.update import PropertyUpdateHandler
from ...handlers.entity.lexeme.update import LexemeUpdateHandler
from ...handlers.entity.wikidata_import import EntityJsonImportHandler
from ...handlers.entity.read import EntityReadHandler
from ...handlers.entity.update import EntityUpdateHandler

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


@router.put("/item/{entity_id}", response_model=EntityResponse)
async def update_item(
    entity_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing item entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = ItemUpdateHandler()
    # Convert to EntityUpdateRequest
    entity_request = EntityUpdateRequest(**request.model_dump())
    return await handler.update_entity(
        entity_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.put("/property/{entity_id}", response_model=EntityResponse)
async def update_property(
    entity_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing property entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = PropertyUpdateHandler()
    entity_request = EntityUpdateRequest(**request.model_dump())
    entity_request.type = "property"
    return await handler.update_entity(
        entity_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.put("/lexeme/{entity_id}", response_model=EntityResponse)
async def update_lexeme(
    entity_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing lexeme entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = LexemeUpdateHandler()
    entity_request = EntityUpdateRequest(**request.model_dump())
    entity_request.type = "lexeme"
    return await handler.update_entity(
        entity_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.post("/json-import", response_model=EntityJsonImportResponse)
async def import_entities_from_jsonl(
    request: EntityJsonImportRequest, req: Request
) -> EntityJsonImportResponse:
    """Import entities from Wikidata JSONL dump file."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    return await EntityJsonImportHandler.import_entities_from_jsonl(
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.get("/entities/items/{item_id}/labels/{language_code}")
async def get_item_label(item_id: str, language_code: str, req: Request):
    """Get item label for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )
    labels = response.data.get("labels", {})
    if language_code not in labels:
        raise HTTPException(status_code=404, detail=f"Label not found for language {language_code}")
    return labels[language_code]


@router.put("/entities/items/{item_id}/labels/{language_code}")
async def update_item_label(item_id: str, language_code: str, update_data: Dict[str, Any], req: Request) -> EntityResponse:
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
    if "labels" not in current_entity.data:
        current_entity.data["labels"] = {}
    current_entity.data["labels"][language_code] = {
        "language": language_code,
        "value": label_value
    }

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type,
        **current_entity.data
    )

    return await update_handler.update_entity(
        item_id, update_request, clients.vitess, clients.s3,
        clients.stream_producer, validator
    )


@router.delete("/entities/items/{item_id}/labels/{language_code}")
async def delete_item_label(item_id: str, language_code: str, req: Request) -> EntityResponse:
    """Delete item label for language."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Check if label exists
    labels = current_entity.data.get("labels", {})
    if language_code not in labels:
        # Idempotent - return current entity if label doesn't exist
        return current_entity

    # Remove label
    del current_entity.data["labels"][language_code]

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type,
        **current_entity.data
    )

    return await update_handler.update_entity(
        item_id, update_request, clients.vitess, clients.s3,
        clients.stream_producer, validator
    )


@router.get("/entities/items/{item_id}/descriptions/{language_code}")
async def get_item_description(item_id: str, language_code: str, req: Request):
    """Get item description for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )
    descriptions = response.data.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(status_code=404, detail=f"Description not found for language {language_code}")
    return descriptions[language_code]


@router.put("/entities/items/{item_id}/descriptions/{language_code}")
async def update_item_description(item_id: str, language_code: str, update_data: Dict[str, Any], req: Request) -> EntityResponse:
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
    if "descriptions" not in current_entity.data:
        current_entity.data["descriptions"] = {}
    current_entity.data["descriptions"][language_code] = {
        "language": language_code,
        "value": description_value
    }

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type,
        **current_entity.data
    )

    return await update_handler.update_entity(
        item_id, update_request, clients.vitess, clients.s3,
        clients.stream_producer, validator
    )


@router.delete("/entities/items/{item_id}/descriptions/{language_code}")
async def delete_item_description(item_id: str, language_code: str, req: Request) -> EntityResponse:
    """Delete item description for language."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Check if description exists
    descriptions = current_entity.data.get("descriptions", {})
    if language_code not in descriptions:
        # Idempotent - return current entity if description doesn't exist
        return current_entity

    # Remove description
    del current_entity.data["descriptions"][language_code]

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type,
        **current_entity.data
    )

    return await update_handler.update_entity(
        item_id, update_request, clients.vitess, clients.s3,
        clients.stream_producer, validator
    )


@router.get("/entities/items/{item_id}/aliases/{language_code}")
async def get_item_aliases_for_language(item_id: str, language_code: str, req: Request):
    """Get item aliases for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(status_code=404, detail=f"Aliases not found for language {language_code}")
    return aliases[language_code]


@router.patch("/entities/items/{item_id}/aliases/{language_code}")
async def patch_item_aliases_for_language(item_id: str, language_code: str, patch_data: Dict[str, Any], req: Request) -> EntityResponse:
    """Patch item aliases for language using JSON Patch."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(item_id, clients.vitess, clients.s3)

    # Get current aliases for the language
    current_aliases = current_entity.data.get("aliases", {}).get(language_code, [])

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
                    raise HTTPException(status_code=400, detail=f"Invalid index: {index}")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported path: {path}")
        elif op == "replace":
            if path.startswith("/") and path[1:].isdigit():
                index = int(path[1:])
                if 0 <= index < len(updated_aliases):
                    updated_aliases[index] = value
                else:
                    raise HTTPException(status_code=400, detail=f"Invalid index: {index}")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported path: {path}")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {op}")

    # Update entity data
    if "aliases" not in current_entity.data:
        current_entity.data["aliases"] = {}
    current_entity.data["aliases"][language_code] = updated_aliases

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.data.get("type") or "item"
    update_request = EntityUpdateRequest(
        type=entity_type,
        **current_entity.data
    )

    return await update_handler.update_entity(
        item_id, update_request, clients.vitess, clients.s3,
        clients.stream_producer, validator
    )
