"""Qualifiers routes for fetching deduplicated qualifiers."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.data.rest_api.v1.entitybase.response import (
    QualifierResponse,
    ReconstructedSnakValue,
)
from models.data.rest_api.v1.entitybase.response.misc2 import (
    SerializableQualifierValue,
)
from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler

logger = logging.getLogger(__name__)

ProcessedQualifierValue = (
    ReconstructedSnakValue
    | int
    | str
    | list[ReconstructedSnakValue | int | str]
)

qualifiers_router = APIRouter(prefix="/qualifiers", tags=["statements"])


def _validate_and_parse_hashes(hashes: str) -> list[int]:
    """Validate and parse hash strings into integers."""
    hash_list = [h.strip() for h in hashes.split(",") if h.strip()]
    if not hash_list:
        raise HTTPException(status_code=400, detail="No hashes provided")
    if len(hash_list) > 100:
        raise HTTPException(status_code=400, detail="Too many hashes (max 100)")
    try:
        return [int(h) for h in hash_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hash format")


def _reconstruct_snak_value(value: int | str, snak_handler: SnakHandler) -> ReconstructedSnakValue | int | str:
    """Reconstruct snak from hash if value is a hash, otherwise return as-is."""
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        reconstructed_snak = snak_handler.get_snak(int(value))
        if reconstructed_snak:
            return ReconstructedSnakValue(**reconstructed_snak)
        logger.warning(f"Snak {value} not found")
        return value
    return value


# noinspection PyTypeHints
def _process_qualifier_value(qual_value: Any, snak_handler: SnakHandler) -> ProcessedQualifierValue:
    """Process qualifier value, handling both single values and lists."""
    if isinstance(qual_value, list):
        return [_reconstruct_snak_value(item, snak_handler) for item in qual_value]
    return _reconstruct_snak_value(qual_value, snak_handler)


def _build_qualifier_response(item: S3QualifierData, snak_handler: SnakHandler) -> QualifierResponse:
    """Build qualifier response with reconstructed snaks."""
    qualifier_dict = {}
    for prop_key, qual_values in item.qualifier.items():
        processed = _process_qualifier_value(qual_values, snak_handler)
        qualifier_dict[prop_key] = _convert_to_serializable(processed).value
    return QualifierResponse(
        qualifier=qualifier_dict,
        hash=item.content_hash,
        created_at=item.created_at,
    )


# noinspection PyTypeHints
def _convert_to_serializable(value: ProcessedQualifierValue) -> SerializableQualifierValue:
    """Convert ReconstructedSnakValue objects back to dicts for JSON serialization."""
    if isinstance(value, ReconstructedSnakValue):
        return SerializableQualifierValue(value=value.model_dump())
    if isinstance(value, list):
        converted_list = []
        for item in value:
            if isinstance(item, ReconstructedSnakValue):
                converted_list.append(item.model_dump())
            else:
                converted_list.append(item)
        return SerializableQualifierValue(value=converted_list)
    return SerializableQualifierValue(value=value)


@qualifiers_router.get("/{hashes}")
async def get_qualifiers(req: Request, hashes: str) -> list[QualifierResponse | None]:
    """Fetch qualifiers by hash(es).

    Supports single hash (e.g., /qualifiers/123) or comma-separated batch (e.g., /qualifiers/123,456,789).

    Returns array of qualifier dicts in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    rapidhashes = _validate_and_parse_hashes(hashes)

    try:
        result = state.s3_client.load_qualifiers_batch(rapidhashes)
        snak_handler = SnakHandler(state=state)

        qualifiers: list[QualifierResponse | None] = []
        for item in result:
            if item is None:
                qualifiers.append(None)
            else:
                qualifiers.append(_build_qualifier_response(item, snak_handler))
        
        return qualifiers
    except Exception as e:
        logger.error(f"Failed to load qualifiers {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
