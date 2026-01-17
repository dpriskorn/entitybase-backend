from _typeshed import Incomplete
from rdflib.graph import Graph, _ContextType, _TriplePatternType, _TripleType
from rdflib.plugins.sparql.sparql import Query, Update
from rdflib.query import Result
from rdflib.store import Store
from rdflib.term import Identifier, URIRef
from typing import Any, Generator, Iterator, Mapping

__all__ = ["SimpleMemory", "Memory"]

class SimpleMemory(Store):
    identifier: Incomplete
    def __init__(
        self, configuration: str | None = None, identifier: Identifier | None = None
    ) -> None: ...
    def add(
        self, triple: _TripleType, context: _ContextType, quoted: bool = False
    ) -> None: ...
    def remove(
        self, triple_pattern: _TriplePatternType, context: _ContextType | None = None
    ) -> None: ...
    def triples(
        self, triple_pattern: _TriplePatternType, context: _ContextType | None = None
    ) -> Iterator[tuple[_TripleType, Iterator[_ContextType | None]]]: ...
    def __len__(self, context: _ContextType | None = None) -> int: ...
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None: ...
    def namespace(self, prefix: str) -> URIRef | None: ...
    def prefix(self, namespace: URIRef) -> str | None: ...
    def namespaces(self) -> Iterator[tuple[str, URIRef]]: ...
    def query(
        self,
        query: Query | str,
        initNs: Mapping[str, Any],
        initBindings: Mapping[str, Identifier],
        queryGraph: str,
        **kwargs: Any,
    ) -> Result: ...
    def update(
        self,
        update: Update | str,
        initNs: Mapping[str, Any],
        initBindings: Mapping[str, Identifier],
        queryGraph: str,
        **kwargs: Any,
    ) -> None: ...

class Memory(Store):
    context_aware: bool
    formula_aware: bool
    graph_aware: bool
    identifier: Incomplete
    def __init__(
        self, configuration: str | None = None, identifier: Identifier | None = None
    ) -> None: ...
    def add(
        self, triple: _TripleType, context: _ContextType, quoted: bool = False
    ) -> None: ...
    def remove(
        self, triple_pattern: _TriplePatternType, context: _ContextType | None = None
    ) -> None: ...
    def triples(
        self, triple_pattern: _TriplePatternType, context: _ContextType | None = None
    ) -> Generator[
        tuple[_TripleType, Generator[_ContextType | None, None, None]], None, None
    ]: ...
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None: ...
    def namespace(self, prefix: str) -> URIRef | None: ...
    def prefix(self, namespace: URIRef) -> str | None: ...
    def namespaces(self) -> Iterator[tuple[str, URIRef]]: ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def __len__(self, context: _ContextType | None = None) -> int: ...
    def add_graph(self, graph: Graph) -> None: ...
    def remove_graph(self, graph: Graph) -> None: ...
    def query(
        self,
        query: Query | str,
        initNs: Mapping[str, Any],
        initBindings: Mapping[str, Identifier],
        queryGraph: str,
        **kwargs,
    ) -> Result: ...
    def update(
        self,
        update: Update | Any,
        initNs: Mapping[str, Any],
        initBindings: Mapping[str, Identifier],
        queryGraph: str,
        **kwargs,
    ) -> None: ...
