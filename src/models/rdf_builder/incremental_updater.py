"""Incremental RDF updater for diff-based updates."""

from pydantic import BaseModel

from models.internal_representation.entity_data import EntityData
from models.rdf_builder.diffs import (
    DiffResult,
    StatementDiff,
    TermsDiff,
    SitelinksDiff,
    EntityDiffs,
)


class IncrementalRDFUpdater(BaseModel):
    """Handles incremental RDF updates via diffs."""

    entity_id: str
    current_rdf: str = ""

    def apply_diffs(self, diffs: EntityDiffs) -> None:
        """Apply diffs to the current RDF."""
        # Simplified: just append diff info to RDF string
        # In real impl, parse RDF and modify triples
        self._apply_statement_diffs(diffs.statements)
        self._apply_terms_diffs(diffs.terms)
        self._apply_sitelinks_diffs(diffs.sitelinks)

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
    def compute_diffs(old_entity: EntityData, new_entity: EntityData) -> EntityDiffs:
        """Compute diffs between two entities."""
        return EntityDiffs(
            statements=StatementDiff.compute(
                old_entity.statements, new_entity.statements
            ),
            terms=TermsDiff.compute(
                old_entity.labels, new_entity.labels
            ),  # Simplify: just labels
            sitelinks=SitelinksDiff.compute(
                old_entity.sitelinks or {}, new_entity.sitelinks or {}
            ),
        )
