"""Lexeme endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import LexemeCreateHandler

logger = logging.getLogger(__name__)
from models.rest_api.entitybase.v1.request import EntityCreateRequest
from models.rest_api.entitybase.v1.response import EntityResponse

router = APIRouter()


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
