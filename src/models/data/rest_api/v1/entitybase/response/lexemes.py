"""Response models for lexeme forms, lemmas, and senses endpoints."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class RepresentationData(BaseModel):
    language: str = Field(..., description="Language code")
    value: str = Field(..., description="Representation text value")
    model_config = ConfigDict(frozen=True)


class LemmaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: str = Field(..., description="Lemma text value")


class LemmasResponse(BaseModel):
    lemmas: Dict[str, RepresentationData] = Field(
        default_factory=dict, description="Lemmas by language code"
    )


class FormResponse(BaseModel):
    id: str = Field(..., description="Form ID")
    representations: Dict[str, RepresentationData] = Field(
        default_factory=dict, description="Representations by language"
    )
    grammatical_features: List[str] = Field(
        default_factory=list, alias="grammaticalFeatures", description="Grammatical features"
    )
    claims: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict, description="Form claims/statements"
    )
    model_config = ConfigDict(frozen=True)


class SenseResponse(BaseModel):
    id: str = Field(..., description="Sense ID")
    glosses: Dict[str, RepresentationData] = Field(
        default_factory=dict, description="Glosses by language"
    )
    claims: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict, description="Sense claims/statements"
    )
    model_config = ConfigDict(frozen=True)


class FormsResponse(BaseModel):
    forms: List[FormResponse] = Field(
        default_factory=list, description="List of lexeme forms"
    )


class SensesResponse(BaseModel):
    senses: List[SenseResponse] = Field(
        default_factory=list, description="List of lexeme senses"
    )


class FormRepresentationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: str = Field(..., description="Form representation value")


class FormRepresentationsResponse(BaseModel):
    representations: Dict[str, RepresentationData] = Field(
        default_factory=dict, description="Form representations by language"
    )
    model_config = ConfigDict(extra="forbid")


class SenseGlossesResponse(BaseModel):
    glosses: Dict[str, RepresentationData] = Field(
        default_factory=dict, description="Sense glosses by language"
    )
    model_config = ConfigDict(extra="forbid")


class SenseGlossResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: str = Field(..., description="Gloss text value")


class LexemeLanguageResponse(BaseModel):
    """Response model for lexeme language endpoint."""

    model_config = ConfigDict(extra="forbid")
    language: str = Field(..., description="Lexeme language code (QID)")


class LexemeLexicalCategoryResponse(BaseModel):
    """Response model for lexeme lexical category endpoint."""

    model_config = ConfigDict(extra="forbid")
    lexical_category: str = Field(..., description="Lexeme lexical category (QID)")
