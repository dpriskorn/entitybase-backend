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
        form_dict_copy = form_dict.copy()
        if "id" not in form_dict_copy:
            form_dict_copy["id"] = ""
        if "grammaticalFeatures" not in form_dict_copy:
            form_dict_copy["grammaticalFeatures"] = []
        if "claims" not in form_dict_copy:
            form_dict_copy["claims"] = {}
        if "representations" not in form_dict_copy:
            form_dict_copy["representations"] = {}

        form = Form().from_json(form_dict_copy)
        if form.id and "-" in form.id:
            suffix = form.id.split("-")[-1]
            if suffix.startswith("F"):
                try:
                    num = int(suffix[1:])
                    max_form_num = max(max_form_num, num)
                except ValueError:
                    pass
        wbi_forms.append(form)

    forms_list = []
    for form in wbi_forms:
        if not form.id:
            max_form_num += 1
            form.id = f"{lexeme_id}-F{max_form_num}"
        forms_list.append(form.get_json())

    return Forms().from_json(forms_list)


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
        sense_dict_copy = sense_dict.copy()
        if "id" not in sense_dict_copy:
            sense_dict_copy["id"] = ""
        if "glosses" not in sense_dict_copy:
            sense_dict_copy["glosses"] = {}
        if "claims" not in sense_dict_copy:
            sense_dict_copy["claims"] = {}

        sense = Sense().from_json(sense_dict_copy)
        if sense.id and "-" in sense.id:
            suffix = sense.id.split("-")[-1]
            if suffix.startswith("S"):
                try:
                    num = int(suffix[1:])
                    max_sense_num = max(max_sense_num, num)
                except ValueError:
                    pass
        wbi_senses.append(sense)

    senses_list = []
    for sense in wbi_senses:
        if not sense.id:
            max_sense_num += 1
            sense.id = f"{lexeme_id}-S{max_sense_num}"
        senses_list.append(sense.get_json())

    return Senses().from_json(senses_list)
