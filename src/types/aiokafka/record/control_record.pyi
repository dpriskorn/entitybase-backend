from _typeshed import Incomplete
from dataclasses import dataclass
from typing_extensions import Self

@dataclass(frozen=True)
class ControlRecord:
    version: int
    type_: int
    def __eq__(self, other: object) -> bool: ...
    __hash__ = ...
    @classmethod
    def parse(cls, data: bytes) -> Self: ...

ABORT_MARKER: Incomplete
COMMIT_MARKER: Incomplete
