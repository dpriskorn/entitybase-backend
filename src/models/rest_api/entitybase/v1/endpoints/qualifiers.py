"""Qualifiers routes for fetching deduplicated qualifiers."""

import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models.rest_api.entitybase.v1.response.qualifiers_references import (
    QualifierResponse,
)

logger = logging.getLogger(__name__)

qualifiers_router = APIRouter(prefix="/qualifiers", tags=["statements"])


@qualifiers_router.get("/{hashes}")
async def get_qualifiers(req: Request, hashes: str) -> list[QualifierResponse | None]:
    """Fetch qualifiers by hash(es).

    Supports single hash (e.g., /qualifiers/123) or comma-separated batch (e.g., /qualifiers/123,456,789).

    Returns array of qualifier dicts in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.clients
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
        result = state.s3_client.load_qualifiers_batch(rapidhashes)
        # Convert S3QualifierData to QualifierResponse models
        return [
            QualifierResponse(
                qualifier=item.qualifier,
                hash=item.content_hash,
                created_at=item.created_at,
            )
            if item is not None
            else None
            for item in result
        ]
    except Exception as e:
        logger.error(f"Failed to load qualifiers {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
