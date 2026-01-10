from pydantic import ConfigDict
"""Entity reference value type."""

from typing_extensions import Literal
from .base import Value


class EntityValue(Value):
    """Value representing a reference to another Wikibase entity."""

    kind: Literal["entity"] = "entity"
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#WikibaseItem"

    model_config = ConfigDict(frozen=True)
