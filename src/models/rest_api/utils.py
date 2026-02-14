"""Validation utilities for REST API."""

import logging
import re
from typing import NoReturn

from models.data.infrastructure.s3.enums import EntityType

logger = logging.getLogger(__name__)

QID_PATTERN = re.compile(r"^Q\d+$")


def raise_validation_error(
    message: str,
    status_code: int = 400,
) -> NoReturn:
    """Raise HTTPException for validation errors.

    Always raises HTTPException regardless of environment for consistent
    HTTP error responses.

    NOTE: Always use this function instead of raising ValidationError directly
    to ensure proper HTTP error handling for user responses.
    """
    logger.info(f"Raising validation error: {message} with status {status_code}")
    from fastapi import HTTPException

    raise HTTPException(status_code=status_code, detail=message)


def infer_entity_type_from_id(entity_id: str) -> EntityType | None:
    """Infer entity type from ID format.

    Returns:
        EntityType.ITEM for Q\\d+
        EntityType.PROPERTY for P\\d+
        EntityType.LEXEME for L\\d+
        None if invalid format
    """
    if re.match(r"^Q\d+$", entity_id):
        return EntityType.ITEM
    elif re.match(r"^P\d+$", entity_id):
        return EntityType.PROPERTY
    elif re.match(r"^L\d+$", entity_id):
        return EntityType.LEXEME
    return None


def validate_qid(value: str, field_name: str) -> None:
    """Validate that a value is a valid QID format (Q followed by digits)."""
    if not value:
        raise_validation_error(
            f"{field_name} is required for lexeme creation.",
            status_code=400,
        )
    if not QID_PATTERN.match(value):
        raise_validation_error(
            f"{field_name} must be a valid QID format (Q followed by digits), got: {value}",
            status_code=400,
        )
