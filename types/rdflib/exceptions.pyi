from _typeshed import Incomplete
from typing import Any

__all__ = ["Error", "ParserError", "UniquenessError"]

class Error(Exception):
    msg: Incomplete
    def __init__(self, msg: str | None = None) -> None: ...

class ParserError(Error):
    msg: str
    def __init__(self, msg: str) -> None: ...

class UniquenessError(Error):
    def __init__(self, values: Any) -> None: ...
