"""Utility functions for lexeme endpoints."""

import re

from fastapi import HTTPException


def _parse_form_id(form_id: str) -> tuple[str, str]:
    """Parse form ID and extract lexeme ID and form suffix.

    Args:
        form_id: Form ID like "L42-F1" or "F1"

    Returns:
        Tuple of (lexeme_id, form_suffix) like ("L42", "F1")

    Raises:
        HTTPException: If format is invalid
    """
    full_match = re.match(r"^(L\d+)-(F\d+)$", form_id)
    if full_match:
        return full_match.group(1), full_match.group(2)

    short_match = re.match(r"^(F\d+)$", form_id)
    if short_match:
        return "", short_match.group(1)

    raise HTTPException(
        status_code=400, detail="Invalid form ID format. Use L42-F1 or F1"
    )


def _parse_sense_id(sense_id: str) -> tuple[str, str]:
    """Parse sense ID and extract lexeme ID and sense suffix.

    Args:
        sense_id: Sense ID like "L42-S1" or "S1"

    Returns:
        Tuple of (lexeme_id, sense_suffix) like ("L42", "S1")

    Raises:
        HTTPException: If format is invalid
    """
    full_match = re.match(r"^(L\d+)-(S\d+)$", sense_id)
    if full_match:
        return full_match.group(1), full_match.group(2)

    short_match = re.match(r"^(S\d+)$", sense_id)
    if short_match:
        return "", short_match.group(1)

    raise HTTPException(
        status_code=400, detail="Invalid sense ID format. Use L42-S1 or S1"
    )


def _extract_numeric_suffix(suffix: str) -> int:
    """Extract numeric value from form/sense suffix like 'F1' -> 1."""
    return int(suffix[1:])
