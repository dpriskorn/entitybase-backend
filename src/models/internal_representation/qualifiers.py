"""Internal representation of Wikibase qualifiers."""

from pydantic import BaseModel, ConfigDict

from models.internal_representation.values.base import Value


class Qualifier(BaseModel):
    """Qualifier providing additional context to a statement."""

    property: str
    value: Value

    model_config = ConfigDict(frozen=True)
