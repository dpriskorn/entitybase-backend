"""Diff result model for incremental RDF updates."""

from typing import Any, List

from pydantic import BaseModel


class DiffResult(BaseModel):
    """Result of diffing two entities."""

    added: List[Any] = []
    removed: List[Any] = []
    modified: List[dict[str, Any]] = []
