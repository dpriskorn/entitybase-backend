"""Property creation endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.property import PropertyCreateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/properties", response_model=EntityResponse)
async def create_property(
    request: EntityCreateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Create a new property entity."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator
    enumeration_service = req.app.state.state_handler.enumeration_service
    handler = PropertyCreateHandler(
        state=state, enumeration_service=enumeration_service
    )
    return await handler.create_entity(  # type: ignore[no-any-return]
        request=request,
        edit_headers=headers,
        validator=validator,
    )
