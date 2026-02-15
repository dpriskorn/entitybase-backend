"""Utility functions for lexeme endpoints."""

import re
from typing import Any

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


def assign_form_ids(lexeme_id: str, forms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assign IDs to forms missing them, using incrementing numbers.

    This mimics Wikibase behavior where deleted form IDs are never reused.

    Args:
        lexeme_id: The lexeme ID (e.g., "L42")
        forms: List of form dictionaries, some may lack "id"

    Returns:
        List of form dictionaries with IDs assigned to those missing them
    """
    max_form_num = 0

    for form in forms:
        form_id = form.get("id", "")
        if "-" in form_id:
            suffix = form_id.split("-")[-1]
            if suffix.startswith("F"):
                try:
                    num = int(suffix[1:])
                    max_form_num = max(max_form_num, num)
                except ValueError:
                    pass

    result = []
    for form in forms:
        if "id" not in form or not form.get("id"):
            max_form_num += 1
            new_form = form.copy()
            new_form["id"] = f"{lexeme_id}-F{max_form_num}"
            result.append(new_form)
        else:
            result.append(form)

    return result


def assign_sense_ids(lexeme_id: str, senses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assign IDs to senses missing them, using incrementing numbers.

    This mimics Wikibase behavior where deleted sense IDs are never reused.

    Args:
        lexeme_id: The lexeme ID (e.g., "L42")
        senses: List of sense dictionaries, some may lack "id"

    Returns:
        List of sense dictionaries with IDs assigned to those missing them
    """
    max_sense_num = 0

    for sense in senses:
        sense_id = sense.get("id", "")
        if "-" in sense_id:
            suffix = sense_id.split("-")[-1]
            if suffix.startswith("S"):
                try:
                    num = int(suffix[1:])
                    max_sense_num = max(max_sense_num, num)
                except ValueError:
                    pass

    result = []
    for sense in senses:
        if "id" not in sense or not sense.get("id"):
            max_sense_num += 1
            new_sense = sense.copy()
            new_sense["id"] = f"{lexeme_id}-S{max_sense_num}"
            result.append(new_sense)
        else:
            result.append(sense)

    return result
