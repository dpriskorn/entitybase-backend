"""Reference routes for fetching deduplicated references."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models.data.rest_api.v1.entitybase.response import (
    ReferenceResponse,
)
from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler

logger = logging.getLogger(__name__)


def _reconstruct_reference_snaks(
    reference_dict: dict, snak_handler: SnakHandler
) -> dict:
    """Reconstruct snaks from hashes in a reference dictionary.

    Args:
        reference_dict: Reference dictionary containing snaks with potential hash values
        snak_handler: SnakHandler instance for loading snak data

    Returns:
        Reference dictionary with reconstructed snaks
    """
    if "snaks" not in reference_dict:
        return reference_dict

    reconstructed_snaks = {}
    for prop_key, snak_values in reference_dict["snaks"].items():
        if isinstance(snak_values, list):
            new_snak_values = []
            for snak_item in snak_values:
                if isinstance(snak_item, int) or (
                    isinstance(snak_item, str) and snak_item.isdigit()
                ):
                    reconstructed_snak = snak_handler.get_snak(int(snak_item))
                    if reconstructed_snak:
                        new_snak_values.append(reconstructed_snak)
                    else:
                        logger.warning(f"Snak {snak_item} not found")
                else:
                    new_snak_values.append(snak_item)
            reconstructed_snaks[prop_key] = new_snak_values
        elif isinstance(snak_values, int) or (
            isinstance(snak_values, str) and snak_values.isdigit()
        ):
            reconstructed_snak = snak_handler.get_snak(int(snak_values))
            if reconstructed_snak:
                reconstructed_snaks[prop_key] = [reconstructed_snak]
            else:
                logger.warning(f"Snak {snak_values} not found")
        else:
            reconstructed_snaks[prop_key] = snak_values

    reference_dict["snaks"] = reconstructed_snaks
    return reference_dict


references_router = APIRouter(prefix="/references", tags=["statements"])


@references_router.get("/{hashes}")
async def get_references(req: Request, hashes: str) -> List[ReferenceResponse | None]:
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
        snak_handler = SnakHandler(state=state)

        references: List[ReferenceResponse | None] = []
        for item in result:
            if item is None:
                references.append(None)
                continue

            reference_dict = _reconstruct_reference_snaks(
                item.reference.copy(), snak_handler
            )

            references.append(
                ReferenceResponse(
                    reference=reference_dict,
                    hash=item.content_hash,
                    created_at=item.created_at,
                )
            )

        return references
    except Exception as e:
        logger.error(f"Failed to load references {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
