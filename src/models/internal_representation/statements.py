from pydantic import BaseModel, ConfigDict

from models.internal_representation.ranks import Rank
from models.internal_representation.values import Value
from models.internal_representation.qualifiers import Qualifier
from models.internal_representation.references import Reference


class Statement(BaseModel):
    property: str
    value: Value
    rank: Rank
    qualifiers: list[Qualifier]
    references: list[Reference]
    statement_id: str

    model_config = ConfigDict(frozen=True)
