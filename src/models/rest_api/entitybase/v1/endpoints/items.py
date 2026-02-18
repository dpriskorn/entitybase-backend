"""Item creation endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entities/items", response_model=EntityResponse)
async def create_item(
    request: EntityCreateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Create a new item entity."""
    logger.info(
        f"🔍 ENDPOINT: Received create request for {request.id or 'auto-assign'}"
    )
    logger.debug(f"🔍 ENDPOINT: Request data: {request.model_dump()}")

    try:
        state = req.app.state.state_handler
        if not hasattr(state, "vitess_client") or not hasattr(state, "validator"):
            raise_validation_error("State handler not available", status_code=503)
        validator = req.app.state.state_handler.validator
        enumeration_service = req.app.state.state_handler.enumeration_service

        logger.debug(
            f"🔍 ENDPOINT: Services available - state: {state is not None}, validator: {validator is not None}, enum_svc: {enumeration_service is not None}"
        )

        handler = ItemCreateHandler(
            state=state, enumeration_service=enumeration_service
        )
        logger.info("🔍 ENDPOINT: Handler created, calling create_entity")

        result = await handler.create_entity(
            request, edit_headers=headers, validator=validator
        )
        logger.info(f"🔍 ENDPOINT: Entity creation successful: {result.id}")
        return result

    except Exception as e:
        logger.error(f"🔍 ENDPOINT: Create item failed: {e}", exc_info=True)
        raise
