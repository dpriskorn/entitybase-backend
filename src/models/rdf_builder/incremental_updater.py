"""Incremental RDF updater for diff-based updates."""

from typing import Dict

from pydantic import BaseModel

from models.rdf_builder.diffs import DiffResult, StatementDiff, TermsDiff, SitelinksDiff


class IncrementalRDFUpdater(BaseModel):
    """Handles incremental RDF updates via diffs."""

    entity_id: str
    current_rdf: str = ""

    def apply_diffs(self, diffs: Dict[str, DiffResult]) -> None:
        """Apply diffs to the current RDF."""
        # Simplified: just append diff info to RDF string
        # In real impl, parse RDF and modify triples
        for component, diff in diffs.items():
            if component == "statements":
                self._apply_statement_diffs(diff)
            elif component == "terms":
                self._apply_terms_diffs(diff)
            elif component == "sitelinks":
                self._apply_sitelinks_diffs(diff)

    def _apply_statement_diffs(self, diff: DiffResult) -> None:
        # Add/remove statement triples
        for stmt in diff.added:
            self.current_rdf += f"\n# Added statement: {stmt}"
        for stmt in diff.removed:
            self.current_rdf += f"\n# Removed statement: {stmt}"

    def _apply_terms_diffs(self, diff: DiffResult) -> None:
        # Add/remove term triples
        for term in diff.added:
            self.current_rdf += f"\n# Added term: {term}"
        for term in diff.removed:
            self.current_rdf += f"\n# Removed term: {term}"

    def _apply_sitelinks_diffs(self, diff: DiffResult) -> None:
        # Add/remove sitelink triples
        for link in diff.added:
            self.current_rdf += f"\n# Added sitelink: {link}"
        for link in diff.removed:
            self.current_rdf += f"\n# Removed sitelink: {link}"

    def get_updated_rdf(self) -> str:
        """Get the updated RDF string."""
        return self.current_rdf

    @staticmethod
    def compute_diffs(old_entity: "EntityData", new_entity: "EntityData") -> Dict[str, DiffResult]:
        """Compute diffs between two entities."""
        return {
            "statements": StatementDiff.compute(old_entity.statements, new_entity.statements),
            "terms": TermsDiff.compute(old_entity.labels, new_entity.labels),  # Simplify: just labels
            "sitelinks": SitelinksDiff.compute(old_entity.sitelinks or {}, new_entity.sitelinks or {}),
        }