"""Hash resolution routes for fetching deduplicated data by hash."""

import logging
from typing import Any, List, Optional, cast

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.data.rest_api.v1.entitybase.response import (
    BatchAliasesResponse,
    BatchDescriptionsResponse,
    BatchLabelsResponse,
    BatchSitelinksResponse,
    QualifierResponse,
    ReconstructedSnakValue,
    ReferenceResponse,
    SnakResponse,
    StatementResponse,
)
from models.data.rest_api.v1.entitybase.response.misc2 import (
    SerializableQualifierValue,
)
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler

logger = logging.getLogger(__name__)

ProcessedQualifierValue = (
    ReconstructedSnakValue | int | str | list[ReconstructedSnakValue | int | str]
)

resolve_router = APIRouter(prefix="/resolve", tags=["resolve"])


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


@resolve_router.get("/qualifiers/{hashes}")
async def get_qualifiers(req: Request, hashes: str) -> list[QualifierResponse | None]:
    """Fetch qualifiers by hash(es).

    Supports single hash (e.g., /resolve/qualifiers/123) or comma-separated batch
    (e.g., /resolve/qualifiers/123,456,789).

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


def _reconstruct_snak_value(
    value: int | str, snak_handler: SnakHandler
) -> ReconstructedSnakValue | int | str:
    """Reconstruct snak from hash if value is a hash, otherwise return as-is."""
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        reconstructed_snak = snak_handler.get_snak(int(value))
        if reconstructed_snak:
            return ReconstructedSnakValue(**reconstructed_snak)
        logger.warning(f"Snak {value} not found")
        return value
    return value


def _process_qualifier_value(
    qual_value: Any, snak_handler: SnakHandler
) -> ProcessedQualifierValue:
    """Process qualifier value, handling both single values and lists."""
    if isinstance(qual_value, list):
        return [_reconstruct_snak_value(item, snak_handler) for item in qual_value]
    return _reconstruct_snak_value(qual_value, snak_handler)


def _build_qualifier_response(
    item: S3QualifierData, snak_handler: SnakHandler
) -> QualifierResponse:
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


def _convert_to_serializable(
    value: ProcessedQualifierValue,
) -> SerializableQualifierValue:
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


@resolve_router.get("/references/{hashes}")
async def get_references(req: Request, hashes: str) -> List[ReferenceResponse | None]:
    """Fetch references by hash(es).

    Supports single hash (e.g., /resolve/references/123) or comma-separated batch
    (e.g., /resolve/references/123,456,789).

    Returns array of reference dicts in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    rapidhashes = _validate_and_parse_hashes(hashes)

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


@resolve_router.get("/snaks/{hashes}")
async def get_snaks(req: Request, hashes: str) -> list[SnakResponse | None]:
    """Fetch snaks by hash(es).

    Supports single hash (e.g., /resolve/snaks/123) or comma-separated batch
    (e.g., /resolve/snaks/123,456,789).

    Returns array of snak dicts in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    rapidhashes = _validate_and_parse_hashes(hashes)

    try:
        result = state.s3_client.load_snaks_batch(rapidhashes)
        return [
            SnakResponse(
                snak=item.snak,
                hash=item.content_hash,
                created_at=item.created_at,
            )
            if item is not None
            else None
            for item in result
        ]
    except Exception as e:
        logger.error(f"Failed to load snaks {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@resolve_router.get("/statements/{hashes}")
async def get_statements(req: Request, hashes: str) -> list[StatementResponse | None]:
    """Fetch statements by hash(es).

    Supports single hash (e.g., /resolve/statements/123) or comma-separated batch
    (e.g., /resolve/statements/123,456,789).

    Returns array of statement dicts in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    rapidhashes = _validate_and_parse_hashes(hashes)

    try:
        handler = StatementHandler(state=state)
        return handler.get_statements_batch(rapidhashes)
    except Exception as e:
        logger.error(f"Failed to load statements {rapidhashes}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@resolve_router.get("/glosses/{hashes}")
async def get_glosses(req: Request, hashes: str) -> list[Optional[str]]:
    """Fetch sense glosses by hash(es).

    Supports single hash (e.g., /resolve/glosses/123) or comma-separated batch
    (e.g., /resolve/glosses/123,456,789).

    Returns array of gloss strings in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    rapidhashes = _validate_and_parse_hashes(hashes)

    try:
        result = state.s3_client.load_sense_glosses_batch(rapidhashes)
        return cast(list[str | None], result)
    except Exception as e:
        logger.error(f"Failed to load glosses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@resolve_router.get("/representations/{hashes}")
async def get_representations(req: Request, hashes: str) -> list[Optional[str]]:
    """Fetch form representations by hash(es).

    Supports single hash (e.g., /resolve/representations/123) or comma-separated batch
    (e.g., /resolve/representations/123,456,789).

    Returns array of representation strings in request order; null for missing hashes.
    Max 100 hashes per request.
    """
    state = req.app.state.state_handler
    rapidhashes = _validate_and_parse_hashes(hashes)

    try:
        result = state.s3_client.load_form_representations_batch(rapidhashes)
        return cast(list[str | None], result)
    except Exception as e:
        logger.error(f"Failed to load representations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@resolve_router.get("/labels/{hashes}", response_model=BatchLabelsResponse)
async def get_batch_labels(hashes: str, req: Request) -> BatchLabelsResponse:
    """Get batch labels by hashes.

    Supports single hash (e.g., /resolve/labels/123) or comma-separated batch
    (e.g., /resolve/labels/123,456,789).

    Returns dict mapping hash strings to label text. Max 20 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result: dict[str, str] = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            label = state.s3_client.load_metadata("labels", hash_value)
            if label:
                result[h] = label.data
        except (ValueError, S3NotFoundError):
            pass
    return BatchLabelsResponse(labels=result)


@resolve_router.get("/descriptions/{hashes}", response_model=BatchDescriptionsResponse)
async def get_batch_descriptions(
    hashes: str, req: Request
) -> BatchDescriptionsResponse:
    """Get batch descriptions by hashes.

    Supports single hash (e.g., /resolve/descriptions/123) or comma-separated batch
    (e.g., /resolve/descriptions/123,456,789).

    Returns dict mapping hash strings to description text. Max 20 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result: dict[str, str] = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            desc = state.s3_client.load_metadata("descriptions", hash_value)
            if desc:
                result[h] = desc.data
        except (ValueError, S3NotFoundError):
            pass
    return BatchDescriptionsResponse(descriptions=result)


@resolve_router.get("/aliases/{hashes}", response_model=BatchAliasesResponse)
async def get_batch_aliases(hashes: str, req: Request) -> BatchAliasesResponse:
    """Get batch aliases by hashes.

    Supports single hash (e.g., /resolve/aliases/123) or comma-separated batch
    (e.g., /resolve/aliases/123,456,789).

    Returns dict mapping hash strings to alias text lists. Max 20 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result: dict[str, list[str]] = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            aliases = state.s3_client.load_metadata("aliases", hash_value)
            if aliases:
                result[h] = aliases.data
        except (ValueError, S3NotFoundError):
            pass
    return BatchAliasesResponse(aliases=result)


@resolve_router.get("/sitelinks/{hashes}", response_model=BatchSitelinksResponse)
async def get_batch_sitelinks(hashes: str, req: Request) -> BatchSitelinksResponse:
    """Get batch sitelink titles by hashes.

    Supports single hash (e.g., /resolve/sitelinks/123) or comma-separated batch
    (e.g., /resolve/sitelinks/123,456,789).

    Returns dict mapping hash strings to sitelink titles. Max 20 hashes per request.
    """
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result: dict[str, str] = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            title = state.s3_client.load_sitelink_metadata(hash_value)
            if title:
                result[h] = title
        except (ValueError, S3NotFoundError):
            pass
    return BatchSitelinksResponse(sitelinks=result)
