"""Item creation endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Request

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.response import EntityIdResult
from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/entities/items", response_model=OperationResult[EntityIdResult])
async def create_item(
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[EntityIdResult]:
    """Create a new empty item entity."""
    logger.info("🔍 ENDPOINT: Received GET request to create item")

    try:
        state = req.app.state.state_handler
        if not hasattr(state, "vitess_client") or not hasattr(state, "validator"):
            raise_validation_error("State handler not available", status_code=503)
        validator = req.app.state.state_handler.validator
        enumeration_service = req.app.state.state_handler.enumeration_service

        request = EntityCreateRequest(type="item")

        handler = ItemCreateHandler(
            state=state, enumeration_service=enumeration_service
        )
        logger.debug("🔍 ENDPOINT: Handler created, calling create_entity")

        result = await handler.create_entity(
            request, edit_headers=headers, validator=validator
        )
        logger.info(f"🔍 ENDPOINT: Item creation successful: {result.id}")

        return OperationResult(
            success=True,
            data=EntityIdResult(entity_id=result.id, revision_id=result.revision_id),
        )

    except Exception as e:
        logger.error(f"🔍 ENDPOINT: Create item failed: {e}", exc_info=True)
        raise
