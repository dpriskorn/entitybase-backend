from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class URLValue(Value):
    kind: Literal["url"] = Field(default="url", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#Url"

    model_config = ConfigDict(frozen=True)
