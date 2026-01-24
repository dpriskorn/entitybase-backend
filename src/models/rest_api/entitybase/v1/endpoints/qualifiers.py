"""Qualifiers routes for fetching deduplicated qualifiers."""

import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models.data.rest_api.v1.entitybase.response import (
    QualifierResponse,
)
from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler

logger = logging.getLogger(__name__)

qualifiers_router = APIRouter(prefix="/qualifiers", tags=["statements"])


@qualifiers_router.get("/{hashes}")
async def get_qualifiers(req: Request, hashes: str) -> list[QualifierResponse | None]:
    """Fetch qualifiers by hash(es).

    Supports single hash (e.g., /qualifiers/123) or comma-separated batch (e.g., /qualifiers/123,456,789).

    Returns array of qualifier dicts in request order; null for missing hashes.
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
        result = state.s3_client.load_qualifiers_batch(rapidhashes)
        snak_handler = SnakHandler(state=state)
        
        qualifiers = []
        for item in result:
            if item is None:
                qualifiers.append(None)
                continue
            
            # Reconstruct snaks from hashes
            qualifier_dict = {}
            for prop_key, qual_values in item.qualifier.items():
                if isinstance(qual_values, list):
                    new_qual_values = []
                    for qual_item in qual_values:
                        if isinstance(qual_item, int) or (isinstance(qual_item, str) and qual_item.isdigit()):
                            reconstructed_snak = snak_handler.get_snak(int(qual_item))
                            if reconstructed_snak:
                                new_qual_values.append(reconstructed_snak)
                            else:
                                logger.warning(f"Snak {qual_item} not found")
                        else:
                            new_qual_values.append(qual_item)
                    qualifier_dict[prop_key] = new_qual_values
                elif isinstance(qual_values, int) or (isinstance(qual_values, str) and qual_values.isdigit()):
                    reconstructed_snak = snak_handler.get_snak(int(qual_values))
                    if reconstructed_snak:
                        qualifier_dict[prop_key] = reconstructed_snak
                    else:
                        logger.warning(f"Snak {qual_values} not found")
                else:
                    qualifier_dict[prop_key] = qual_values
            
            qualifiers.append(
                QualifierResponse(
                    qualifier=qualifier_dict,
                    hash=item.content_hash,
                    created_at=item.created_at,
                )
            )
        
        return qualifiers
    except Exception as e:
        logger.error(f"Failed to load qualifiers {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
