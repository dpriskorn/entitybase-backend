"""Lexeme terms models for database records."""

from typing import Dict

from pydantic import BaseModel, Field
from pydantic.root_model import RootModel


class TermHashes(RootModel[Dict[str, str]]):
    """Hash map for term values by language code."""


class FormTermHashes(RootModel[Dict[str, TermHashes]]):
    """Hash map for form term hashes by form ID."""


class SenseTermHashes(RootModel[Dict[str, TermHashes]]):
    """Hash map for sense term hashes by sense ID."""


class LexemeTerms(BaseModel):
    """Container for lexeme terms including forms and senses."""

    forms: FormTermHashes = Field(description="Term hashes for forms")
    senses: SenseTermHashes = Field(description="Term hashes for senses")
