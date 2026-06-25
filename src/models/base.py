"""Custom base class for all project classes."""

from abc import ABC


class Base(ABC):
    """Base class for project classes.

    All non-Pydantic classes should inherit from this class
    instead of using plain class definitions.
    """

    pass
