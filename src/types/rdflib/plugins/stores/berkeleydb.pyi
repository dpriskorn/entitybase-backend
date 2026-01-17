from _typeshed import Incomplete
from berkeleydb import db
from rdflib.graph import Graph, _ContextType, _TriplePatternType, _TripleType
from rdflib.store import Store
from rdflib.term import Identifier, Node, URIRef
from typing import Any, Callable, Generator

__all__ = [
    "BerkeleyDB",
    "_ToKeyFunc",
    "_FromKeyFunc",
    "_GetPrefixFunc",
    "_ResultsFromKeyFunc",
]

_ToKeyFunc = Callable[[tuple[bytes, bytes, bytes], bytes], bytes]
_FromKeyFunc = Callable[[bytes], tuple[bytes, bytes, bytes, bytes]]
_GetPrefixFunc = Callable[
    [tuple[str, str, str], str | None], Generator[str, None, None]
]
_ResultsFromKeyFunc = Callable[
    [bytes, Node | None, Node | None, Node | None, bytes],
    tuple[tuple[Node, Node, Node], Generator[Node, None, None]],
]

class BerkeleyDB(Store):
    context_aware: bool
    formula_aware: bool
    transaction_aware: bool
    graph_aware: bool
    db_env: db.DBEnv
    def __init__(
        self, configuration: str | None = None, identifier: Identifier | None = None
    ) -> None: ...
    identifier: Incomplete
    def is_open(self) -> bool: ...
    def open(
        self, configuration: str | tuple[str, str], create: bool = True
    ) -> int | None: ...
    def sync(self) -> None: ...
    def close(self, commit_pending_transaction: bool = False) -> None: ...
    def add(
        self,
        triple: _TripleType,
        context: _ContextType,
        quoted: bool = False,
        txn: Any | None = None,
    ) -> None: ...
    def remove(
        self,
        spo: _TriplePatternType,
        context: _ContextType | None,
        txn: Any | None = None,
    ) -> None: ...
    def triples(
        self,
        spo: _TriplePatternType,
        context: _ContextType | None = None,
        txn: Any | None = None,
    ) -> Generator[
        tuple[_TripleType, Generator[_ContextType | None, None, None]], None, None
    ]: ...
    def __len__(self, context: _ContextType | None = None) -> int: ...
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None: ...
    def namespace(self, prefix: str) -> URIRef | None: ...
    def prefix(self, namespace: URIRef) -> str | None: ...
    def namespaces(self) -> Generator[tuple[str, URIRef], None, None]: ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def add_graph(self, graph: Graph) -> None: ...
    def remove_graph(self, graph: Graph): ...
