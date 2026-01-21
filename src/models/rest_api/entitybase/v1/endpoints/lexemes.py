"""Lexeme endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)

from models.rest_api.entitybase.v1.request import EntityCreateRequest
from models.rest_api.entitybase.v1.response import EntityResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/lexemes", response_model=EntityResponse)
async def create_lexeme(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new lexeme entity."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator
    enumeration_service = req.app.state.state_handler.enumeration_service
    handler = LexemeCreateHandler(enumeration_service=enumeration_service, state=state)
    return await handler.create_entity(  # type: ignore[no-any-return]
        request,
        validator,
    )
