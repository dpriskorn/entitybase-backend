from pydantic import BaseModel, ConfigDict
"""Internal representation of Wikibase qualifiers."""

from models.internal_representation.values import Value

from pydantic import BaseModel, ConfigDict


class Qualifier(BaseModel):
    """Qualifier providing additional context to a statement."""

    property: str
    value: Value

    model_config = ConfigDict(frozen=True)
