"""Lexeme endpoints for Entitybase v1 API."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.handlers.entity.lexeme.create import LexemeCreateHandler

logger = logging.getLogger(__name__)
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.handlers.entity.update import EntityUpdateHandler, LexemeUpdateHandler
from models.rest_api.entitybase.request import EntityCreateRequest, EntityUpdateRequest
from models.rest_api.entitybase.response import EntityResponse
from models.rest_api.entitybase.response.misc import (
    AliasesResponse,
    DescriptionResponse,
    LabelResponse,
    )


@router.put("/entities/lexemes/{lexeme_id}", response_model=EntityResponse)
async def update_lexeme(
    lexeme_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing lexeme entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = LexemeUpdateHandler()
    entity_request = EntityUpdateRequest(**request.model_dump())
    entity_request.type = "lexeme"
    return await handler.update_entity(
        lexeme_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )




@router.post("/entities/lexemes", response_model=EntityResponse)
async def create_lexeme(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new lexeme entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = LexemeCreateHandler(enumeration_service)
    return await handler.create_entity(  # type: ignore[no-any-return]
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )
