"""Reference routes for fetching deduplicated references."""

import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models.data.rest_api.v1.response import (
    ReferenceResponse,
)

logger = logging.getLogger(__name__)

references_router = APIRouter(prefix="/references", tags=["statements"])


@references_router.get("/{hashes}")
async def get_references(req: Request, hashes: str) -> list[ReferenceResponse | None]:
    """Fetch references by hash(es).

    Supports single hash (e.g., /references/123) or comma-separated batch (e.g., /references/123,456,789).

    Returns array of reference dicts in request order; null for missing hashes.
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
        result = state.s3_client.load_references_batch(rapidhashes)
        # Convert S3ReferenceData to ReferenceResponse models
        return [
            ReferenceResponse(
                reference=item.reference,
                hash=item.content_hash,
                created_at=item.created_at,
            )
            if item is not None
            else None
            for item in result
        ]
    except Exception as e:
        logger.error(f"Failed to load references {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
