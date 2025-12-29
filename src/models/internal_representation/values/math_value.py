from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class MathValue(Value):
    kind: Literal["math"] = Field(default="math", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#Math"

    model_config = ConfigDict(frozen=True)
