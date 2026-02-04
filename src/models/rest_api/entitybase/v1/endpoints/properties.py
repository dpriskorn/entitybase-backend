"""Property endpoints for Entitybase v1 API."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request

from models.common import EditHeadersType
from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    AliasesResponse,
    DescriptionResponse,
    LabelResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.property import PropertyCreateHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler

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


@router.get(
    "/entities/properties/{property_id}/labels/{language_code}",
    response_model=LabelResponse,
)
async def get_property_label(
    property_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get property label for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(property_id)
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
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(property_id)
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
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(property_id)
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    return AliasesResponse(aliases=aliases[language_code])


@router.put(
    "/entities/properties/{property_id}/aliases/{language_code}",
    response_model=EntityResponse,
)
async def put_property_aliases_for_language(
    property_id: str,
    language_code: str,
    aliases_data: List[str],
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update property aliases for language."""
    logger.debug(
        f"Updating aliases for property {property_id}, language {language_code}"
    )
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Update aliases using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    return await update_handler.update_aliases(
        property_id,
        language_code,
        aliases_data,
        headers,
        validator,
    )
