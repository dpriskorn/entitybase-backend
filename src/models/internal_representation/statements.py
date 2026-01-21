from pydantic import BaseModel, ConfigDict

from models.rdf_builder.models.rdf_statement import RDFStatement

"""Internal representation of Wikibase statements."""

from models.internal_representation.ranks import Rank
from models.internal_representation.values.base import Value
from models.internal_representation.qualifiers import Qualifier
from models.internal_representation.references import Reference


class Statement(BaseModel):
    """Internal representation of a Wikibase statement."""

    property: str
    value: Value
    rank: Rank
    qualifiers: list[Qualifier]
    references: list[Reference]
    statement_id: str

    model_config = ConfigDict(frozen=True)

    def get_rdfstatement(self) -> RDFStatement:
        return RDFStatement(
            guid=self.statement_id,
            property_id=self.property,
            value=self.value,
            rank=self.rank.value,
            qualifiers=self.qualifiers,
            references=self.references,
        )
