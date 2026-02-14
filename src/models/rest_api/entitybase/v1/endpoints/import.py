"""Import routes."""

import logging

from fastapi import APIRouter, Request

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.create import EntityCreateHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.rest_api.utils import raise_validation_error

import_router = APIRouter(tags=["import"])


@import_router.post(
    "/import",
    response_model=EntityResponse,
    summary="Import a single entity (item, property, or lexeme)",
)
async def import_entity(
    request: EntityCreateRequest,
    req: Request,
) -> EntityResponse:
    """Import a single entity of any type.

    This unified endpoint accepts items, properties, and lexemes.
    The entity type is determined by the 'type' field in the request.

    Supported entity types:
    - item: Q-prefixed entities (e.g., Q42)
    - property: P-prefixed entities (e.g., P31)
    - lexeme: L-prefixed entities (e.g., L123)

    Parameters:
    - id: Entity ID (required for import, auto-assignment not supported)
    - type: Entity type (item, property, lexeme)
    - labels: Language-specific labels
    - descriptions: Language-specific descriptions
    - claims: Statements/claims
    - sitelinks: Site links (items only)
    - forms: Forms (lexemes only)
    - senses: Senses (lexemes only)
    - lemmas: Lemmas (lexemes only)
    - aliases: Aliases

    Returns:
    - EntityResponse with created entity data

    Errors:
    - 409: Entity already exists
    - 400: Validation error
    """
    logger.debug(f"Importing entity: {request.id} of type {request.type}")
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator

    logger.debug("Creating entity handler")
    handler = EntityCreateHandler(state=state)

    edit_headers = EditHeaders.model_validate(
        {"X-User-ID": 0, "X-Edit-Summary": "Bulk import"}
    )

    if request.type == "lexeme":
        logger.debug("Validating lexeme has at least one lemma")
        lemma_count = sum(1 for lang in request.lemmas if lang != "lemma_hashes")
        if lemma_count == 0:
            logger.warning("Lexeme has no lemmas")
            raise_validation_error(
                "A lexeme must have at least one lemma.",
                status_code=400,
            )

    logger.info(f"IMPORT START: id={request.id}, type={request.type}")
    logger.debug(f"IMPORT request data: {request.model_dump()}")
    try:
        result = await handler.create_entity(
            request, edit_headers=edit_headers, validator=validator, auto_assign_id=False
        )
        logger.info(f"IMPORT SUCCESS: id={request.id}")
        return result
    except Exception as e:
        logger.error(f"IMPORT FAILED: id={request.id}, error={type(e).__name__}: {e}", exc_info=True)
        raise
