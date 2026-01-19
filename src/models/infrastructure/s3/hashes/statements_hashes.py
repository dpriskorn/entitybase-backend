"""Statements hashes model."""

from pydantic.root_model import RootModel


class StatementsHashes(RootModel[list[int]]):
    """Hash list for entity statements."""