"""Entity diffs collection model for incremental RDF updates."""

from models.rdf_builder.diff_result import DiffResult
from pydantic import BaseModel


class EntityDiffs(BaseModel):
    """Collection of diffs for an entity."""

    statements: DiffResult
    terms: DiffResult
    sitelinks: DiffResult
