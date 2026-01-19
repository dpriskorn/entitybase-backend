"""Diff models for incremental RDF updates."""

from typing import Any, Dict, List

from pydantic import BaseModel


class DiffResult(BaseModel):
    """Result of diffing two entities."""

    added: List[Any] = []
    removed: List[Any] = []
    modified: List[Dict[str, Any]] = []  # e.g., {"old": stmt, "new": stmt}


class StatementDiff(BaseModel):
    """Diff for statements."""

    @staticmethod
    def compute(old_statements: List[Any], new_statements: List[Any]) -> DiffResult:
        # Simplified: assume statements have ids or hashes
        old_ids = {stmt.id for stmt in old_statements}
        new_ids = {stmt.id for stmt in new_statements}

        added = [stmt for stmt in new_statements if stmt.id not in old_ids]
        removed = [stmt for stmt in old_statements if stmt.id not in new_ids]
        # Modified: compare properties, but simplify
        modified = []

        return DiffResult(added=added, removed=removed, modified=modified)


class TermsDiff(BaseModel):
    """Diff for terms (labels, descriptions, aliases)."""

    @staticmethod
    def compute(old_terms: Dict[str, Any], new_terms: Dict[str, Any]) -> DiffResult:
        # Simplified diff for terms dict
        added = {k: v for k, v in new_terms.items() if k not in old_terms}
        removed = {k: v for k, v in old_terms.items() if k not in new_terms}
        modified = {k: {"old": old_terms[k], "new": v} for k, v in new_terms.items() if k in old_terms and old_terms[k] != v}

        return DiffResult(added=list(added.values()), removed=list(removed.values()), modified=list(modified.values()))


class SitelinksDiff(BaseModel):
    """Diff for sitelinks."""

    @staticmethod
    def compute(old_sitelinks: Dict[str, str], new_sitelinks: Dict[str, str]) -> DiffResult:
        added = {k: v for k, v in new_sitelinks.items() if k not in old_sitelinks}
        removed = {k: v for k, v in old_sitelinks.items() if k not in new_sitelinks}
        modified = {k: {"old": old_sitelinks[k], "new": v} for k, v in new_sitelinks.items() if k in old_sitelinks and old_sitelinks[k] != v}

        return DiffResult(added=list(added.values()), removed=list(removed.values()), modified=list(modified.values()))