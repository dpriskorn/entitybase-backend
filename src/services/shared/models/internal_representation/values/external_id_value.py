from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class ExternalIDValue(Value):
    kind: Literal["external_id"] = Field(default="external_id", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#ExternalId"

    model_config = ConfigDict(frozen=True)
