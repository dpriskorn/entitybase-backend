"""Alias endpoints for Entitybase v1 API."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/entities/{entity_id}/aliases/{language_code}",
    response_model=List[str],
)
async def get_entity_aliases(
    entity_id: str, language_code: str, req: Request
) -> list[str]:
    """Get entity alias texts for language."""
    logger.info(f"Getting aliases for entity {entity_id}, language {language_code}")
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(entity_id)

    aliases_hashes = response.entity_data.revision.get("hashes", {}).get("aliases", {})
    if language_code not in aliases_hashes:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )

    alias_texts = []
    for hash_value in aliases_hashes[language_code]:
        alias_data = state.s3_client.load_metadata("labels", int(hash_value))
        if alias_data and alias_data.data:
            alias_texts.append(str(alias_data.data))
    return alias_texts


@router.put(
    "/entities/{entity_id}/aliases/{language_code}", response_model=EntityResponse
)
async def update_entity_aliases(
    entity_id: str,
    language_code: str,
    aliases_data: List[str],
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Update entity aliases for language."""
    logger.info(
        f"📝 ALIASES UPDATE: Starting aliases update for entity={entity_id}, language={language_code}"
    )
    logger.debug(f"📝 ALIASES UPDATE: New aliases count: {len(aliases_data)}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_aliases(
        entity_id,
        language_code,
        aliases_data,
        headers,
        validator,
    )

    return result


@router.post(
    "/entities/{entity_id}/aliases/{language_code}", response_model=EntityResponse
)
async def add_entity_alias(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Add a single alias to entity for language."""
    logger.info(
        f"📝 ALIAS ADD: Starting alias add for entity={entity_id}, language={language_code}"
    )

    if request.language != language_code:
        raise HTTPException(
            status_code=400,
            detail=f"Language in request body ({request.language}) does not match path parameter ({language_code})",
        )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.add_alias(
        entity_id,
        language_code,
        request.value,
        headers,
        validator,
    )

    return result


@router.delete(
    "/entities/{entity_id}/aliases/{language_code}", response_model=EntityResponse
)
async def delete_entity_aliases(
    entity_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> EntityResponse:
    """Delete all aliases for entity language."""
    logger.info(
        f"🗑️ ALIASES DELETE: Starting aliases deletion for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.delete_aliases(
        entity_id,
        language_code,
        headers,
        validator,
    )

    return result
