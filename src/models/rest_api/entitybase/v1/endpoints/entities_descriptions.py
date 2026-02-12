"""Description endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, HTTPException, Request, Response
from starlette.responses import JSONResponse

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
from models.data.rest_api.v1.entitybase.request.entity import TermUpdateContext
from models.data.rest_api.v1.entitybase.response import DescriptionResponse
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/entities/{entity_id}/descriptions/{language_code}",
    response_model=DescriptionResponse,
)
async def get_entity_description(
    entity_id: str, language_code: str, req: Request
) -> DescriptionResponse:
    """Get entity description hash for language."""
    logger.info(
        f"Getting description for entity {entity_id}, language {language_code}"
    )
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(entity_id)

    descriptions_hashes = response.entity_data.revision.get("hashes", {}).get(
        "descriptions", {}
    )
    if language_code not in descriptions_hashes:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )

    return DescriptionResponse(value=descriptions_hashes[language_code])


@router.put("/entities/{entity_id}/descriptions/{language_code}")
async def update_entity_description(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Update entity description for language."""
    logger.info(
        f"📝 DESCRIPTION UPDATE: Starting description update for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_description(
        entity_id,
        context,
        headers,
        validator,
    )

    response_dict = result.model_dump(mode="json", by_alias=True)
    return JSONResponse(content=response_dict)


@router.delete("/entities/{entity_id}/descriptions/{language_code}")
async def delete_entity_description(
    entity_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Delete entity description for language."""
    logger.info(
        f"🗑️ DESCRIPTION DELETE: Starting description deletion for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.delete_description(
        entity_id,
        language_code,
        headers,
        validator,
    )

    response_dict = result.model_dump(mode="json", by_alias=True)
    return JSONResponse(content=response_dict)


@router.post("/entities/{entity_id}/descriptions/{language_code}")
async def add_entity_description(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Add a new description to entity for language (alias for PUT)."""
    logger.info(
        f"📝 DESCRIPTION ADD: Starting description add for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_description(
        entity_id,
        context,
        headers,
        validator,
    )

    response_dict = result.model_dump(mode="json", by_alias=True)
    return JSONResponse(content=response_dict)
