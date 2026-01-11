"""Lexeme endpoints for Entitybase v1 API."""

from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request

from ...handlers.entity.lexeme.create import LexemeCreateHandler
from ...handlers.entity.read import EntityReadHandler
from ...handlers.entity.update import EntityUpdateHandler
from ...request import EntityCreateRequest, EntityUpdateRequest
from ...response import EntityResponse
from ...response.misc import AliasesResponse, DescriptionResponse, LabelResponse

router = APIRouter()


@router.post("/entities/lexemes", response_model=EntityResponse)
async def create_lexeme(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new lexeme entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = LexemeCreateHandler(enumeration_service)
    return await handler.create_entity(  # type: ignore[return]
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.get(
    "/entities/lexemes/{lexeme_id}/labels/{language_code}", response_model=LabelResponse
)
async def get_lexeme_label(
    lexeme_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get lexeme label for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(lexeme_id, clients.vitess, clients.s3)
    labels = response.data.get("labels", {})
    if language_code not in labels:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    return LabelResponse(value=labels[language_code])


@router.get(
    "/entities/lexemes/{lexeme_id}/descriptions/{language_code}",
    response_model=DescriptionResponse,
)
async def get_lexeme_description(
    lexeme_id: str, language_code: str, req: Request
) -> DescriptionResponse:
    """Get lexeme description for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(lexeme_id, clients.vitess, clients.s3)
    descriptions = response.data.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )
    return DescriptionResponse(value=descriptions[language_code])


@router.get(
    "/entities/lexemes/{lexeme_id}/aliases/{language_code}",
    response_model=AliasesResponse,
)
async def get_lexeme_aliases_for_language(
    lexeme_id: str, language_code: str, req: Request
) -> AliasesResponse:
    """Get lexeme aliases for language."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(lexeme_id, clients.vitess, clients.s3)
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    return AliasesResponse(aliases=aliases[language_code])


@router.patch("/entities/lexemes/{lexeme_id}/aliases/{language_code}")
async def patch_lexeme_aliases_for_language(
    lexeme_id: str, language_code: str, patch_data: Dict[str, Any], req: Request
) -> EntityResponse:
    """Patch lexeme aliases for language using JSON Patch."""
    clients = req.app.state.clients
    validator = req.app.state.validator

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(lexeme_id, clients.vitess, clients.s3)

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

    return await update_handler.update_entity(  # type: ignore[return]
        lexeme_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )
