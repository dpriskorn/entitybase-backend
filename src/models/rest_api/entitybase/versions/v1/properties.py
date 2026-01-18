"""Property endpoints for Entitybase v1 API."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.handlers.entity.property import PropertyCreateHandler

logger = logging.getLogger(__name__)
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.handlers.entity.update import EntityUpdateHandler, PropertyUpdateHandler
from models.rest_api.entitybase.request import EntityCreateRequest, EntityUpdateRequest
from models.rest_api.entitybase.response import EntityResponse
from models.rest_api.entitybase.response.misc import (
    AliasesResponse,
    DescriptionResponse,
    LabelResponse,
)

router = APIRouter()


@router.post("/entities/properties", response_model=EntityResponse)
async def create_property(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new property entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = PropertyCreateHandler(enumeration_service)
    return await handler.create_entity(  # type: ignore[no-any-return]
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.put("/entities/properties/{property_id}", response_model=EntityResponse)
async def update_property(
    property_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing property entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = PropertyUpdateHandler()
    entity_request = EntityUpdateRequest(**request.model_dump())
    entity_request.type = "property"
    return await handler.update_entity(
        property_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.get(
    "/entities/properties/{property_id}/labels/{language_code}",
    response_model=LabelResponse,
)
async def get_property_label(
    property_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get property label for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(property_id, clients.vitess, clients.s3)
    labels = response.data.get("labels", {})
    if language_code not in labels:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    return LabelResponse(value=labels[language_code])


@router.get(
    "/entities/properties/{property_id}/descriptions/{language_code}",
    response_model=DescriptionResponse,
)
async def get_property_description(
    property_id: str, language_code: str, req: Request
) -> DescriptionResponse:
    """Get property description for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(property_id, clients.vitess, clients.s3)
    descriptions = response.data.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )
    return DescriptionResponse(value=descriptions[language_code])


@router.get(
    "/entities/properties/{property_id}/aliases/{language_code}",
    response_model=AliasesResponse,
)
async def get_property_aliases_for_language(
    property_id: str, language_code: str, req: Request
) -> AliasesResponse:
    """Get property aliases for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(property_id, clients.vitess, clients.s3)
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    return AliasesResponse(aliases=aliases[language_code])


@router.patch("/entities/properties/{property_id}/aliases/{language_code}")
async def patch_property_aliases_for_language(
    property_id: str, language_code: str, patch_data: Dict[str, Any], req: Request
) -> EntityResponse:
    """Patch property aliases for language using JSON Patch."""
    logger.debug(
        f"Patching aliases for property {property_id}, language {language_code}"
    )
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
    if "aliases" not in current_entity.data:
        current_entity.data["aliases"] = {}
    current_entity.data["aliases"][language_code] = updated_aliases

    # Create new revision
    update_handler = EntityUpdateHandler()
    update_request = EntityUpdateRequest(
        type=current_entity.data.get("type"), **current_entity.data
    )

    return await update_handler.update_entity(
        property_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )
