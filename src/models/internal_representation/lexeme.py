"""Lexeme-specific models for forms and senses."""

from typing import Dict, List, Any

from pydantic import BaseModel, ConfigDict, Field


class FormRepresentation(BaseModel):
    """Model for form representation in a specific language."""

    model_config = ConfigDict(frozen=True)

    language: str = Field(description="Language code (e.g., 'en', 'de')")
    value: str = Field(description="The written form of the word")


class LexemeForm(BaseModel):
    """Model for a grammatical form of a lexeme."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(
        pattern=r"^L[0-9]+-F[0-9]+$",
        description="Form ID in format L{numeric_id}-F{form_number}"
    )
    representations: Dict[str, FormRepresentation] = Field(
        default_factory=dict,
        description="Written representations in different languages"
    )
    grammatical_features: List[str] = Field(
        default_factory=list,
        alias="grammaticalFeatures",
        description="List of grammatical feature item IDs (e.g., ['Q110786'])"
    )
    claims: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Raw claims data for this specific form"
    )


class SenseGloss(BaseModel):
    """Model for sense gloss in a specific language."""

    model_config = ConfigDict(frozen=True)

    language: str = Field(description="Language code (e.g., 'en', 'de')")
    value: str = Field(description="Definition/gloss text")


class LexemeSense(BaseModel):
    """Model for a sense/meaning of a lexeme."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(
        pattern=r"^L[0-9]+-S[0-9]+$",
        description="Sense ID in format L{numeric_id}-S{sense_number}"
    )
    glosses: Dict[str, SenseGloss] = Field(
        default_factory=dict,
        description="Definitions in different languages"
    )
    claims: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Raw claims data for this specific sense"
    )