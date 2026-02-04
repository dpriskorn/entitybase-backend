"""Statement diff model for incremental RDF updates."""

from typing import Any, List

from models.rdf_builder.diff_result import DiffResult
from pydantic import BaseModel


class StatementDiff(BaseModel):
    """Diff for statements."""

    @staticmethod
    def compute(old_statements: List[Any], new_statements: List[Any]) -> DiffResult:
        old_ids = {stmt.id for stmt in old_statements}
        new_ids = {stmt.id for stmt in new_statements}

        added = [stmt for stmt in new_statements if stmt.id not in old_ids]
        removed = [stmt for stmt in old_statements if stmt.id not in new_ids]
        modified: List[Any] = []

        return DiffResult(added=added, removed=removed, modified=modified)
