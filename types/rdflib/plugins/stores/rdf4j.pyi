from rdflib import Graph as Graph
from rdflib.contrib.rdf4j import RDF4JClient as RDF4JClient, has_httpx as has_httpx
from rdflib.contrib.rdf4j.exceptions import (
    RepositoryNotFoundError as RepositoryNotFoundError,
)
from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID as DATASET_DEFAULT_GRAPH_ID,
    Dataset as Dataset,
    _ContextType,
    _QuadType,
    _TriplePatternType,
    _TripleType,
)
from rdflib.store import Store as Store, VALID_STORE as VALID_STORE
from rdflib.term import (
    BNode as BNode,
    Node as Node,
    URIRef as URIRef,
    Variable as Variable,
)
from typing import Generator, Iterable, Iterator

class RDF4JStore(Store):
    context_aware: bool
    formula_aware: bool
    transaction_aware: bool
    graph_aware: bool
    def __init__(
        self,
        base_url: str,
        repository_id: str,
        configuration: str | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        create: bool = False,
        **kwargs,
    ) -> None: ...
    @property
    def client(self): ...
    @property
    def repo(self): ...
    def open(
        self, configuration: str | tuple[str, str] | None, create: bool = False
    ) -> int | None: ...
    def close(self, commit_pending_transaction: bool = False) -> None: ...
    def add(
        self,
        triple: _TripleType,
        context: _ContextType | None = None,
        quoted: bool = False,
    ) -> None: ...
    def addN(self, quads: Iterable[_QuadType]) -> None: ...
    def remove(
        self, triple: _TriplePatternType, context: _ContextType | None = None
    ) -> None: ...
    def triples(
        self, triple_pattern: _TriplePatternType, context: _ContextType | None = None
    ) -> Iterator[tuple[_TripleType, Iterator[_ContextType | None]]]: ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None: ...
    def prefix(self, namespace: URIRef) -> str | None: ...
    def namespace(self, prefix: str) -> URIRef | None: ...
    def namespaces(self) -> Iterator[tuple[str, URIRef]]: ...
    def add_graph(self, graph: Graph) -> None: ...
    def remove_graph(self, graph: Graph) -> None: ...
    def __len__(self, context: _ContextType | None = None) -> int: ...
