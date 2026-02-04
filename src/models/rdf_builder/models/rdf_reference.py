"""RDF reference model."""
from typing import Any

from pydantic import BaseModel, Field

from models.internal_representation.references import Reference

from models.rest_api.utils import raise_validation_error


class RDFReference(BaseModel):
    """RDF reference model for Turtle generation.

    Concern: Generate reference URI from hash (stored in IR).

    Wikidata uses wdref: prefix with SHA1 hash.
    Example: http://www.wikidata.org/reference/a4d108601216cffd2ff1819ccf12b483486b62e7
    """

    statement_uri: str
    reference: Reference = Field(exclude=True)

    def model_post_init(self, context: Any) -> None:
        if not self.reference.hash:
            raise_validation_error(
                f"Reference has no hash. "
                f"Cannot generate wdref: URI for statement: {self.statement_uri}"
            )

    @property
    def reference_uri(self) -> str:
        """Generate wdref: URI from hash."""
        return f"wdref:{self.reference.hash}"

    @property
    def hash(self) -> str:
        return self.reference.hash