from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class CommonsMediaValue(Value):
    kind: Literal["commons_media"] = Field(default="commons_media", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#CommonsMedia"

    model_config = ConfigDict(frozen=True)
