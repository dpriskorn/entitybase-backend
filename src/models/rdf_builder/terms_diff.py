"""Terms diff model for incremental RDF updates."""

from typing import Any, Dict

from models.rdf_builder.diff_result import DiffResult
from pydantic import BaseModel


class TermsDiff(BaseModel):
    """Diff for terms (labels, descriptions, aliases)."""

    @staticmethod
    def compute(old_terms: Dict[str, Any], new_terms: Dict[str, Any]) -> DiffResult:
        added = {k: v for k, v in new_terms.items() if k not in old_terms}
        removed = {k: v for k, v in old_terms.items() if k not in new_terms}
        modified = {
            k: {"old": old_terms[k], "new": v}
            for k, v in new_terms.items()
            if k in old_terms and old_terms[k] != v
        }

        return DiffResult(
            added=list(added.values()),
            removed=list(removed.values()),
            modified=list(modified.values()),
        )
