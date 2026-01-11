from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import json

from models.rest_api.api.entity import EntityCreateRequest, EntityResponse, EntityUpdateRequest
from ...handlers.entity.property import PropertyCreateHandler
from ...handlers.entity.read import EntityReadHandler
from ...handlers.entity.update import EntityUpdateHandler

router = APIRouter()


@router.post("/entities/properties", response_model=EntityResponse)
async def create_property(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new property entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = PropertyCreateHandler(enumeration_service)
    return await handler.create_entity(
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.get("/entities/properties/{property_id}/labels/{language_code}")
async def get_property_label(property_id: str, language_code: str, req: Request):
    """Get property label for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        property_id, clients.vitess, clients.s3
    )
    labels = response.data.get("labels", {})
    if language_code not in labels:
        raise HTTPException(status_code=404, detail=f"Label not found for language {language_code}")
    return labels[language_code]


@router.get("/entities/properties/{property_id}/descriptions/{language_code}")
async def get_property_description(property_id: str, language_code: str, req: Request):
    """Get property description for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        property_id, clients.vitess, clients.s3
    )
    descriptions = response.data.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(status_code=404, detail=f"Description not found for language {language_code}")
    return descriptions[language_code]


@router.get("/entities/properties/{property_id}/aliases/{language_code}")
async def get_property_aliases_for_language(property_id: str, language_code: str, req: Request):
    """Get property aliases for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        property_id, clients.vitess, clients.s3
    )
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(status_code=404, detail=f"Aliases not found for language {language_code}")
    return aliases[language_code]


@router.patch("/entities/properties/{property_id}/aliases/{language_code}")
async def patch_property_aliases_for_language(property_id: str, language_code: str, patch_data: Dict[str, Any], req: Request) -> EntityResponse:
    """Patch property aliases for language using JSON Patch."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(property_id, clients.vitess, clients.s3)

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
    update_request = EntityUpdateRequest(
        type=current_entity.data.get("type"),
        **current_entity.data
    )

    return await update_handler.update_entity(
        property_id, update_request, clients.vitess, clients.s3,
        clients.stream_producer, validator
    )
