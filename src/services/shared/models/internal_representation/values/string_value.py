from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class StringValue(Value):
    kind: Literal["string"] = Field(default="string", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#String"

    model_config = ConfigDict(frozen=True)
