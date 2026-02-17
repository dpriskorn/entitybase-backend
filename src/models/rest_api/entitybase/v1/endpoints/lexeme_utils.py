"""Utility functions for lexeme endpoints."""

import logging
import re
from typing import Any

from fastapi import HTTPException
from wikibaseintegrator.models.forms import Form, Forms
from wikibaseintegrator.models.senses import Sense, Senses

logger = logging.getLogger(__name__)


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


def _prepare_form_defaults(form_dict: dict[str, Any]) -> dict[str, Any]:
    """Set default values for form fields if missing.

    Args:
        form_dict: Form dictionary to add defaults to

    Returns:
        Form dictionary with all required fields
    """
    form_dict_copy = form_dict.copy()
    form_dict_copy.setdefault("id", "")
    form_dict_copy.setdefault("grammaticalFeatures", [])
    form_dict_copy.setdefault("claims", {})
    form_dict_copy.setdefault("representations", {})
    return form_dict_copy


def _extract_form_number(form_id: str | None) -> int:
    """Extract numeric suffix from form ID (e.g., "L42-F5" -> 5).

    Args:
        form_id: Form ID string

    Returns:
        Numeric suffix, or 0 if not a valid form ID
    """
    if not form_id or "-" not in form_id:
        return 0
    suffix = form_id.split("-")[-1]
    if not suffix.startswith("F"):
        return 0
    try:
        return int(suffix[1:])
    except ValueError:
        return 0


def assign_form_ids(lexeme_id: str, forms: list[dict[str, Any]]) -> Forms:
    """Assign IDs to forms missing them, using incrementing numbers.

    This mimics Wikibase behavior where deleted form IDs are never reused.

    Uses WBI Form model for validation and processing.

    Args:
        lexeme_id: The lexeme ID (e.g., "L42")
        forms: List of form dictionaries, some may lack "id"

    Returns:
        Forms object with IDs assigned to those missing them
    """
    logger.debug(f"Assigning form IDs to {len(forms)} forms for lexeme {lexeme_id}")
    max_form_num = 0

    wbi_forms = []
    for form_dict in forms:
        form_dict_copy = _prepare_form_defaults(form_dict)
        form = Form().from_json(form_dict_copy)
        form_num = _extract_form_number(form.id)
        max_form_num = max(max_form_num, form_num)
        wbi_forms.append(form)

    forms_list = []
    for form in wbi_forms:
        if not form.id:
            max_form_num += 1
            form.id = f"{lexeme_id}-F{max_form_num}"
        forms_list.append(form.get_json())

    return Forms().from_json(forms_list)


def _prepare_sense_defaults(sense_dict: dict[str, Any]) -> dict[str, Any]:
    """Set default values for sense fields if missing.

    Args:
        sense_dict: Sense dictionary to add defaults to

    Returns:
        Sense dictionary with all required fields
    """
    sense_dict_copy = sense_dict.copy()
    sense_dict_copy.setdefault("id", "")
    sense_dict_copy.setdefault("glosses", {})
    sense_dict_copy.setdefault("claims", {})
    return sense_dict_copy


def _extract_sense_number(sense_id: str | None) -> int:
    """Extract numeric suffix from sense ID (e.g., "L42-S5" -> 5).

    Args:
        sense_id: Sense ID string

    Returns:
        Numeric suffix, or 0 if not a valid sense ID
    """
    if not sense_id or "-" not in sense_id:
        return 0
    suffix = sense_id.split("-")[-1]
    if not suffix.startswith("S"):
        return 0
    try:
        return int(suffix[1:])
    except ValueError:
        return 0


def assign_sense_ids(lexeme_id: str, senses: list[dict[str, Any]]) -> Senses:
    """Assign IDs to senses missing them, using incrementing numbers.

    This mimics Wikibase behavior where deleted sense IDs are never reused.

    Uses WBI Sense model for validation and processing.

    Args:
        lexeme_id: The lexeme ID (e.g., "L42")
        senses: List of sense dictionaries, some may lack "id"

    Returns:
        Senses object with IDs assigned to those missing them
    """
    logger.debug(f"Assigning sense IDs to {len(senses)} senses for lexeme {lexeme_id}")
    max_sense_num = 0

    wbi_senses = []
    for sense_dict in senses:
        sense_dict_copy = _prepare_sense_defaults(sense_dict)
        sense = Sense().from_json(sense_dict_copy)
        sense_num = _extract_sense_number(sense.id)
        max_sense_num = max(max_sense_num, sense_num)
        wbi_senses.append(sense)

    senses_list = []
    for sense in wbi_senses:
        if not sense.id:
            max_sense_num += 1
            sense.id = f"{lexeme_id}-S{max_sense_num}"
        senses_list.append(sense.get_json())

    return Senses().from_json(senses_list)
