"""Lexeme endpoints for Entitybase v1 API."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Sub-routers for representations and glosses
representations_router = APIRouter(prefix="/representations", tags=["lexemes"])
glosses_router = APIRouter(prefix="/glosses", tags=["lexemes"])

# Include sub-routers
router.include_router(representations_router)
router.include_router(glosses_router)


@router.post("/entities/lexemes", response_model=EntityResponse)
async def create_lexeme(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new lexeme entity."""
    state = req.app.state.state_handler
    validator = req.app.state.state_handler.validator
    enumeration_service = req.app.state.state_handler.enumeration_service
    handler = LexemeCreateHandler(enumeration_service=enumeration_service, state=state)
    return await handler.create_entity(  # type: ignore[no-any-return]
        request,
        validator,
    )


@representations_router.get("/{hashes}")
async def get_representations(req: Request, hashes: str) -> list[Optional[str]]:
    """Fetch form representations by hash(es).

    Supports single hash (e.g., /representations/123) or comma-separated batch
    (e.g., /representations/123,456,789).

    Returns array of representation strings in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = [h.strip() for h in hashes.split(",") if h.strip()]
    if not hash_list:
        raise HTTPException(status_code=400, detail="No hashes provided")

    if len(hash_list) > 100:
        raise HTTPException(status_code=400, detail="Too many hashes (max 100)")

    try:
        # Convert to int
        rapidhashes = [int(h) for h in hash_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hash format")

    try:
        result = state.s3_client.load_form_representations_batch(rapidhashes)
        return result
    except Exception as e:
        logger.error(f"Failed to load representations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@glosses_router.get("/{hashes}")
async def get_glosses(req: Request, hashes: str) -> list[Optional[str]]:
    """Fetch sense glosses by hash(es).

    Supports single hash (e.g., /glosses/123) or comma-separated batch
    (e.g., /glosses/123,456,789).

    Returns array of gloss strings in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = [h.strip() for h in hashes.split(",") if h.strip()]
    if not hash_list:
        raise HTTPException(status_code=400, detail="No hashes provided")

    if len(hash_list) > 100:
        raise HTTPException(status_code=400, detail="Too many hashes (max 100)")

    try:
        # Convert to int
        rapidhashes = [int(h) for h in hash_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hash format")

    try:
        result = state.s3_client.load_sense_glosses_batch(rapidhashes)
        return result
    except Exception as e:
        logger.error(f"Failed to load glosses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
