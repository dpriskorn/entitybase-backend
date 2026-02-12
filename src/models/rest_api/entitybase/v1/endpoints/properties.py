"""Property endpoints for Entitybase v1 API."""

import logging
from typing import Any, List

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse, Response

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
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
    resolved_aliases: dict[str, list[dict[str, str]]] = {}
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

    return resolved


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
    logger.debug(f"Getting property label for {property_id}, language {language_code}")
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(property_id)

    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, response.entity_data.revision)
    labels = resolved_revision.get("labels", {})
    logger.debug(f"Labels for {property_id}: {list(labels.keys())}")
    if language_code not in labels:
        raise HTTPException(
            status_code=404, detail=f"Label not found for language {language_code}"
        )
    return LabelResponse(value=labels[language_code]["value"])


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

    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, response.entity_data.revision)
    descriptions = resolved_revision.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(
            status_code=404,
            detail=f"Description not found for language {language_code}",
        )
    return DescriptionResponse(value=descriptions[language_code]["value"])


@router.get(
    "/entities/properties/{property_id}/aliases/{language_code}",
    response_model=list[str],
)
async def get_property_aliases_for_language(
    property_id: str, language_code: str, req: Request
) -> list[str]:
    """Get property aliases for language."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    response = handler.get_entity(property_id)

    # Resolve hashes to actual term values
    resolved_revision = _resolve_hashes_to_terms(state, response.entity_data.revision)
    aliases = resolved_revision.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(
            status_code=404, detail=f"Aliases not found for language {language_code}"
        )
    # Extract just the alias text values
    alias_values = [alias["value"] for alias in aliases[language_code]]
    return alias_values


@router.put(
    "/entities/properties/{property_id}/aliases/{language_code}",
)
async def put_property_aliases_for_language(
    property_id: str,
    language_code: str,
    aliases_data: List[str],
    req: Request,
    headers: EditHeadersType,
) -> Response:
    """Update property aliases for language."""
    logger.debug(
        f"Updating aliases for property {property_id}, language {language_code}"
    )
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    # Update aliases using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.update_aliases(
        property_id,
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
