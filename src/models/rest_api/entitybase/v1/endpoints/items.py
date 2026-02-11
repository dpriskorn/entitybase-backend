"""Item creation endpoints for Entitybase v1 API."""

import json
import logging
from typing import Any, List

from fastapi import APIRouter, HTTPException, Request, Response
from starlette.responses import JSONResponse

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import (
    EntityCreateRequest,
    TermUpdateRequest,
)
from models.data.rest_api.v1.entitybase.request.entity import TermUpdateContext
from models.data.rest_api.v1.entitybase.response import (
    DescriptionResponse,
    LabelResponse,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.infrastructure.vitess.repositories.terms import TermsRepository

logger = logging.getLogger(__name__)

router = APIRouter()


def _resolve_hashes_to_terms(state: StateHandler, revision: dict[str, Any]) -> dict[str, Any]:
    """Resolve hashes in revision to actual term values."""
    terms_repo = TermsRepository(vitess_client=state.vitess_client)
    resolved = revision.copy()
    
    # Resolve labels
    hashes = revision.get("hashes", {})
    labels_hashes = hashes.get("labels", {})
    resolved_labels = {}
    for lang, hash_val in labels_hashes.items():
        term_data = terms_repo.get_term(hash_val)
        if term_data:
            term_value, term_type = term_data
            if term_type == "label":
                resolved_labels[lang] = {
                    "language": lang,
                    "value": term_value,
                }
    resolved["labels"] = resolved_labels
    
    # Resolve descriptions
    descriptions_hashes = hashes.get("descriptions", {})
    resolved_descriptions = {}
    for lang, hash_val in descriptions_hashes.items():
        term_data = terms_repo.get_term(hash_val)
        if term_data:
            term_value, term_type = term_data
            if term_type == "description":
                resolved_descriptions[lang] = {
                    "language": lang,
                    "value": term_value,
                }
    resolved["descriptions"] = resolved_descriptions
    
    # Resolve aliases
    aliases_hashes = hashes.get("aliases", {})
    resolved_aliases = {}
    for lang, hash_list in aliases_hashes.items():
        resolved_aliases[lang] = []
        for hash_val in hash_list:
            term_data = terms_repo.get_term(hash_val)
            if term_data:
                term_value, term_type = term_data
                if term_type == "alias":
                    resolved_aliases[lang].append({
                        "language": lang,
                        "value": term_value,
                    })
    resolved["aliases"] = resolved_aliases
    
    # Remove the hashes section since we've resolved all terms
    if "hashes" in resolved:
        del resolved["hashes"]
    
    return resolved


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
        assert isinstance(state, StateHandler)
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


@router.get(
    "/entities/items/{item_id}/labels/{language_code}", response_model=LabelResponse
)
async def get_item_label(
    item_id: str, language_code: str, req: Request
) -> LabelResponse:
    """Get item label for language."""
    logger.info(f"Getting label for item {item_id}, language {language_code}")
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(item_id)
    
    logger.debug(f"Revision structure: {response.entity_data.revision.keys()}")
    logger.debug(f"Hashes structure: {response.entity_data.revision.get('hashes', {}).keys() if 'hashes' in response.entity_data.revision else 'No hashes key'}")
    
    from models.infrastructure.vitess.repositories.terms import TermsRepository
    
    labels_hashes = response.entity_data.revision.get("hashes", {}).get("labels", {})
    logger.debug(f"Labels hashes: {labels_hashes}")
    if language_code not in labels_hashes:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    
    hash_value = labels_hashes[language_code]
    terms_repo = TermsRepository(vitess_client=state.vitess_client)
    term_data = terms_repo.get_term(hash_value)
    logger.debug(f"Term data for hash {hash_value}: {term_data}")
    
    if not term_data:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    
    term_value, term_type = term_data
    if term_type != "label":
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    
    return LabelResponse(value=term_value)


@router.put(
    "/entities/items/{item_id}/labels/{language_code}"
)
async def update_item_label(
    item_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Update item label for language."""
    logger.info(
        f"📝 LABEL UPDATE: Starting label update for item={item_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    # Update label using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_label(
        item_id,
        context,
        headers,
        validator,
    )
    
    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, result.entity_data.revision)
    
    # Create response dict with resolved terms at the top level of data
    response_dict = result.model_dump(mode='json', by_alias=True)
    response_dict['data']['labels'] = resolved_revision.get('labels', {})
    response_dict['data']['descriptions'] = resolved_revision.get('descriptions', {})
    response_dict['data']['aliases'] = resolved_revision.get('aliases', {})
    
    return JSONResponse(content=response_dict)


@router.delete(
    "/entities/items/{item_id}/labels/{language_code}"
)
async def delete_item_label(
    item_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Delete item label for language."""
    logger.info(
        f"🗑️ LABEL DELETE: Starting label deletion for item={item_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Delete label using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.delete_label(
        item_id,
        language_code,
        headers,
        validator,
    )
    
    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, result.entity_data.revision)
    logger.debug(f"Delete item label - resolved labels: {resolved_revision.get('labels', {})}")
    
    # Create response dict with resolved terms at the top level of data
    response_dict = result.model_dump(mode='json', by_alias=True)
    response_dict['data']['labels'] = resolved_revision.get('labels', {})
    response_dict['data']['descriptions'] = resolved_revision.get('descriptions', {})
    response_dict['data']['aliases'] = resolved_revision.get('aliases', {})
    
    return JSONResponse(content=response_dict)


@router.get(
    "/entities/items/{item_id}/descriptions/{language_code}",
    response_model=DescriptionResponse,
)
async def get_item_description(
    item_id: str, language_code: str, req: Request
) -> DescriptionResponse:
    """Get item description for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(item_id)
    
    from models.infrastructure.vitess.repositories.terms import TermsRepository
    
    descriptions_hashes = response.entity_data.revision.get("hashes", {}).get("descriptions", {})
    if language_code not in descriptions_hashes:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )
    
    hash_value = descriptions_hashes[language_code]
    terms_repo = TermsRepository(vitess_client=state.vitess_client)
    term_data = terms_repo.get_term(hash_value)
    
    if not term_data:
        raise HTTPException(
            status_code=404, detail=f"Description not found for language {language_code}"
        )
    
    term_value, term_type = term_data
    if term_type != "description":
        raise HTTPException(
            status_code=404, detail=f"Description not found for language {language_code}"
        )
    
    return DescriptionResponse(value=term_value)


@router.put(
    "/entities/items/{item_id}/descriptions/{language_code}"
)
async def update_item_description(
    item_id: str,
    language_code: str,
    request: TermUpdateRequest,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Update item description for language."""
    logger.info(
        f"📝 DESCRIPTION UPDATE: Starting description update for item={item_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    context = TermUpdateContext(
        language_code=language_code,
        language=request.language,
        value=request.value,
    )

    # Update description using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_description(
        item_id,
        context,
        headers,
        validator,
    )
    
    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, result.entity_data.revision)
    
    # Create response dict with resolved terms at the top level of data
    response_dict = result.model_dump(mode='json', by_alias=True)
    response_dict['data']['labels'] = resolved_revision.get('labels', {})
    response_dict['data']['descriptions'] = resolved_revision.get('descriptions', {})
    response_dict['data']['aliases'] = resolved_revision.get('aliases', {})
    
    return JSONResponse(content=response_dict)


@router.delete(
    "/entities/items/{item_id}/descriptions/{language_code}"
)
async def delete_item_description(
    item_id: str,
    language_code: str,
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Delete item description for language."""
    logger.info(
        f"🗑️ DESCRIPTION DELETE: Starting description deletion for item={item_id}, language={language_code}"
    )

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Delete description using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.delete_description(
        item_id,
        language_code,
        headers,
        validator,
    )
    
    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, result.entity_data.revision)
    
    # Create response dict with resolved terms at the top level of data
    response_dict = result.model_dump(mode='json', by_alias=True)
    response_dict['data']['labels'] = resolved_revision.get('labels', {})
    response_dict['data']['descriptions'] = resolved_revision.get('descriptions', {})
    response_dict['data']['aliases'] = resolved_revision.get('aliases', {})
    
    return JSONResponse(content=response_dict)


@router.get(
    "/entities/items/{item_id}/aliases/{language_code}", response_model=List[str]
)
async def get_item_aliases_for_language(
    item_id: str, language_code: str, req: Request
) -> list[str]:
    """Get item aliases for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(item_id)
    
    from models.infrastructure.vitess.repositories.terms import TermsRepository
    
    aliases_hashes = response.entity_data.revision.get("hashes", {}).get("aliases", {})
    if language_code not in aliases_hashes:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    
    hash_values = aliases_hashes[language_code]
    terms_repo = TermsRepository(vitess_client=state.vitess_client)
    
    aliases_result = []
    for hash_value in hash_values:
        term_data = terms_repo.get_term(hash_value)
        if term_data:
            term_value, term_type = term_data
            if term_type == "alias":
                aliases_result.append(term_value)
    
    if not aliases_result:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    
    return aliases_result


@router.put(
    "/entities/items/{item_id}/aliases/{language_code}"
)
async def put_item_aliases_for_language(
    item_id: str,
    language_code: str,
    aliases_data: List[str],
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Update item aliases for language."""
    logger.info(
        f"📝 ALIASES UPDATE: Starting aliases update for item={item_id}, language={language_code}"
    )
    logger.debug(f"📝 ALIASES UPDATE: New aliases count: {len(aliases_data)}")

    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Update aliases using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_aliases(
        item_id,
        language_code,
        aliases_data,
        headers,
        validator,
    )
    
    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, result.entity_data.revision)
    
    # Create response dict with resolved terms at the top level of data
    response_dict = result.model_dump(mode='json', by_alias=True)
    response_dict['data']['labels'] = resolved_revision.get('labels', {})
    response_dict['data']['descriptions'] = resolved_revision.get('descriptions', {})
    response_dict['data']['aliases'] = resolved_revision.get('aliases', {})
    
    return JSONResponse(content=response_dict)
