from pydantic import BaseModel

from models.workers.entity_diff.enums import CanonicalizationMethod


class EntityDiffRequest(BaseModel):
    """Request to compute diff between two entity versions."""

    entity_id: str
    rdf_content_v1: str
    rdf_content_v2: str
    format: str = "turtle"
    canonicalization_method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015
    from_revision_id: int = 0  # For streaming events
