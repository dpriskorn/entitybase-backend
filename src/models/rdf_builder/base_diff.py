"""Base diff model for incremental RDF updates."""

from typing import Any, Dict

from models.rdf_builder.diff_result import DiffResult
from pydantic import BaseModel


class BaseDiff(BaseModel):
    """Base class for diff operations."""

    @staticmethod
    def _compute_dict_diff(
        old_items: Dict[str, Any], new_items: Dict[str, Any]
    ) -> DiffResult:
        """Compute diff between two dictionaries."""
        added = {k: v for k, v in new_items.items() if k not in old_items}
        removed = {k: v for k, v in old_items.items() if k not in new_items}
        modified = {
            k: {"old": old_items[k], "new": v}
            for k, v in new_items.items()
            if k in old_items and old_items[k] != v
        }

        return DiffResult(
            added=list(added.values()),
            removed=list(removed.values()),
            modified=list(modified.values()),
        )
