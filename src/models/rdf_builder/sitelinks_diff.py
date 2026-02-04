"""Sitelinks diff model for incremental RDF updates."""

from models.rdf_builder.diff_result import DiffResult
from pydantic import BaseModel


class SitelinksDiff(BaseModel):
    """Diff for sitelinks."""

    @staticmethod
    def compute(
        old_sitelinks: dict[str, str], new_sitelinks: dict[str, str]
    ) -> DiffResult:
        added = {k: v for k, v in new_sitelinks.items() if k not in old_sitelinks}
        removed = {k: v for k, v in old_sitelinks.items() if k not in new_sitelinks}
        modified = {
            k: {"old": old_sitelinks[k], "new": v}
            for k, v in new_sitelinks.items()
            if k in old_sitelinks and old_sitelinks[k] != v
        }

        return DiffResult(
            added=list(added.values()),
            removed=list(removed.values()),
            modified=list(modified.values()),
        )
