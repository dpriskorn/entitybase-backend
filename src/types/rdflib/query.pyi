import rdflib.term
from _typeshed import Incomplete
from rdflib.graph import Graph, _TripleType
from rdflib.plugins.sparql.sparql import Query, Update
from rdflib.term import Identifier, Variable
from typing import Any, BinaryIO, IO, Iterator, Mapping, MutableSequence, overload

__all__ = [
    "Processor",
    "UpdateProcessor",
    "Result",
    "ResultRow",
    "ResultParser",
    "ResultSerializer",
    "ResultException",
    "EncodeOnlyUnicode",
]

class Processor:
    def __init__(self, graph: Graph) -> None: ...
    def query(
        self,
        strOrQuery: str | Query,
        initBindings: Mapping[str, Identifier] = {},
        initNs: Mapping[str, Any] = {},
        DEBUG: bool = False,
    ) -> Mapping[str, Any]: ...

class UpdateProcessor:
    def __init__(self, graph: Graph) -> None: ...
    def update(
        self,
        strOrQuery: str | Update,
        initBindings: Mapping[str, Identifier] = {},
        initNs: Mapping[str, Any] = {},
    ) -> None: ...

class ResultException(Exception): ...

class EncodeOnlyUnicode:
    def __init__(self, stream: BinaryIO) -> None: ...
    def write(self, arg) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

class ResultRow(tuple[rdflib.term.Identifier, ...]):
    labels: Mapping[str, int]
    def __new__(cls, values: Mapping[Variable, Identifier], labels: list[Variable]): ...
    def __getattr__(self, name: str) -> Identifier: ...
    def __getitem__(self, name: str | int | Any) -> Identifier: ...
    @overload
    def get(self, name: str, default: Identifier) -> Identifier: ...
    @overload
    def get(self, name: str, default: Identifier | None = ...) -> Identifier | None: ...
    def asdict(self) -> dict[str, Identifier]: ...

class Result:
    type: Incomplete
    vars: list[Variable] | None
    askAnswer: bool | None
    graph: Graph | None
    def __init__(self, type_: str) -> None: ...
    @property
    def bindings(self) -> MutableSequence[Mapping[Variable, Identifier]]: ...
    @bindings.setter
    def bindings(
        self,
        b: MutableSequence[Mapping[Variable, Identifier]]
        | Iterator[Mapping[Variable, Identifier]],
    ) -> None: ...
    @staticmethod
    def parse(
        source: IO | None = None,
        format: str | None = None,
        content_type: str | None = None,
        **kwargs: Any,
    ) -> Result: ...
    def serialize(
        self,
        destination: str | IO | None = None,
        encoding: str = "utf-8",
        format: str = "xml",
        **args: Any,
    ) -> bytes | None: ...
    def __len__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __iter__(self) -> Iterator[_TripleType | bool | ResultRow]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __eq__(self, other: Any) -> bool: ...

class ResultParser:
    def __init__(self) -> None: ...
    def parse(self, source: IO, **kwargs: Any) -> Result: ...

class ResultSerializer:
    result: Incomplete
    def __init__(self, result: Result) -> None: ...
    def serialize(self, stream: IO, encoding: str = "utf-8", **kwargs: Any) -> None: ...
