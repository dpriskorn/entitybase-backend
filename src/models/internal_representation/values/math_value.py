from pydantic import ConfigDict, Field
"""Mathematical expression value type."""

from typing_extensions import Literal
from .base import Value


class MathValue(Value):
    """Value representing a mathematical expression."""

    kind: Literal["math"] = Field(default="math", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#Math"

    model_config = ConfigDict(frozen=True)
