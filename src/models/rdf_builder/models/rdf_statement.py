"""RDF statement model."""
from typing import Any

from pydantic import BaseModel


class RDFStatement(BaseModel):
    """RDF statement model for Turtle generation.

    Concern: Generate statement URI from GUID.

    Wikidata uses wds: prefix with GUID.
    Example: http://www.wikidata.org/entity/statement/Q17948861-F20AC3A5-627-4EC5-93CA-24F0F00C8AA6
    """

    guid: str
    property_id: str
    value: Any
    rank: str
    qualifiers: Any
    references: Any


