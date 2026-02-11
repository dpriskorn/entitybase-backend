"""Internal data models for entity representation."""

from typing import Dict, List, Any

from pydantic import BaseModel, Field

from models.internal_representation.statements import Statement
from models.internal_representation.lexeme import LexemeForm, LexemeSense


class EntityData(BaseModel):
    """Internal data model for entity with nested structures."""

    id: str
    type: str  # Simplified, or use EntityType
    labels: Dict[
        str, Dict[str, str]
    ]  # e.g., {"en": {"language": "en", "value": "Test"}}
    descriptions: Dict[str, Dict[str, str]]
    aliases: Dict[str, List[Dict[str, str]]]
    statements: List[Statement]
    sitelinks: Dict[str, Any] | None = Field(default=None)  # Simplified sitelinks

    # Lexeme-specific fields
    lemmas: Dict[str, Dict[str, str]] | None = Field(default=None)
    lexical_category: str = Field(default="", alias="lexicalCategory")
    language: str = Field(default="")
    forms: List[LexemeForm] | None = Field(default=None)
    senses: List[LexemeSense] | None = Field(default=None)

    model_config = {"frozen": True}
