from typing import List

from pydantic import BaseModel

from models.workers.entity_diff.entity_diff_worker import Triple


class EntityDiffResponse(BaseModel):
    """Response containing the computed diff."""

    entity_id: str
    added_triples: List[Triple]
    removed_triples: List[Triple]
    canonicalization_method: str
    processing_time_ms: int
    triple_count_v1: int
    triple_count_v2: int
