"""Alias endpoints for Entitybase v1 API."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import TermUpdateRequest
from models.data.rest_api.v1.entitybase.response import (
    TermHashResponse,
    TermHashesResponse,
    DeleteResponse,
)
from models.internal_representation.metadata_extractor import MetadataExtractor
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
    "/entities/{entity_id}/aliases/{language_code}", response_model=TermHashesResponse
)
async def update_entity_aliases(
    entity_id: str,
    language_code: str,
    aliases_data: list[str],
    req: Request,
    headers: EditHeadersType,
) -> TermHashesResponse:
    """Update entity aliases for language."""
    logger.info(
        f"ALIAS UPDATE START: entity={entity_id}, lang={language_code}, count={len(aliases_data)}"
    )
    logger.debug(f"ALIAS UPDATE: aliases={aliases_data}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    try:
        result = await update_handler.update_aliases(
            entity_id,
            language_code,
            aliases_data,
            headers,
            validator,
        )
        logger.info(f"ALIAS UPDATE SUCCESS: entity={entity_id}")
        hashes = [MetadataExtractor.hash_string(alias) for alias in aliases_data]
        return TermHashesResponse(hashes=hashes)
    except Exception as e:
        logger.error(
            f"ALIAS UPDATE FAILED: entity={entity_id}, error={type(e).__name__}: {e}",
            exc_info=True,
        )
        raise


@router.post(
    "/entities/{entity_id}/aliases/{language_code}", response_model=TermHashResponse
)
async def add_entity_alias(
    entity_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> TermHashResponse:
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
    await update_handler.add_alias(
        entity_id,
        language_code,
        request.value,
        headers,
        validator,
    )

    hash_value = MetadataExtractor.hash_string(request.value)
    return TermHashResponse(hash=hash_value)


@router.delete(
    "/entities/{entity_id}/aliases/{language_code}", response_model=DeleteResponse
)
async def delete_entity_aliases(
    entity_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> DeleteResponse:
    """Delete all aliases for entity language."""
    logger.info(
        f"🗑️ ALIASES DELETE: Starting aliases deletion for entity={entity_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    update_handler = EntityUpdateHandler(state=state)
    await update_handler.delete_aliases(
        entity_id,
        language_code,
        headers,
        validator,
    )

    return DeleteResponse(success=True)
