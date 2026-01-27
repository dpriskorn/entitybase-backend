"""Statements hashes model."""

from pydantic import RootModel


class StatementsHashes(RootModel[list[int]]):
    """Hash structure for entity statements."""
