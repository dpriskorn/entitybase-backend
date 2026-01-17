from .sparqlconnector import SPARQLConnector
from _typeshed import Incomplete
from rdflib.graph import (
    Graph,
    _ContextIdentifierType,
    _ContextType,
    _ObjectType,
    _PredicateType,
    _QuadType,
    _SubjectType,
    _TripleChoiceType,
    _TriplePatternType,
    _TripleType,
)
from rdflib.plugins.sparql.sparql import Query, Update
from rdflib.plugins.stores.regexmatching import NATIVE_REGEX
from rdflib.query import Result
from rdflib.store import Store
from rdflib.term import Identifier, URIRef
from typing import Any, Generator, Iterable, Iterator, Mapping

__all__ = ["SPARQLUpdateStore", "SPARQLStore"]

class SPARQLStore(SPARQLConnector, Store):
    formula_aware: bool
    transaction_aware: bool
    graph_aware: bool
    regex_matching = NATIVE_REGEX
    node_to_sparql: Incomplete
    nsBindings: dict[str, Any]
    sparql11: Incomplete
    context_aware: Incomplete
    def __init__(
        self,
        query_endpoint: str | None = None,
        sparql11: bool = True,
        context_aware: bool = True,
        node_to_sparql: _NodeToSparql = ...,
        returnFormat: str | None = "xml",
        auth: tuple[str, str] | None = None,
        **sparqlconnector_kwargs,
    ) -> None: ...
    query_endpoint: Incomplete
    def open(
        self, configuration: str | tuple[str, str], create: bool = False
    ) -> int | None: ...
    def create(self, configuration: str) -> None: ...
    def destroy(self, configuration: str) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def add(
        self, _: _TripleType, context: _ContextType = None, quoted: bool = False
    ) -> None: ...
    def addN(self, quads: Iterable[_QuadType]) -> None: ...
    def remove(self, _: _TriplePatternType, context: _ContextType | None) -> None: ...
    def update(
        self,
        query: Update | str,
        initNs: dict[str, Any] = {},
        initBindings: dict[str, Identifier] = {},
        queryGraph: Identifier = None,
        DEBUG: bool = False,
    ) -> None: ...
    debug: Incomplete
    def query(
        self,
        query: Query | str,
        initNs: Mapping[str, Any] | None = None,
        initBindings: Mapping[str, Identifier] | None = None,
        queryGraph: str | None = None,
        DEBUG: bool = False,
    ) -> Result: ...
    def triples(
        self, spo: _TriplePatternType, context: _ContextType | None = None
    ) -> Iterator[tuple[_TripleType, None]]: ...
    def triples_choices(
        self, _: _TripleChoiceType, context: _ContextType | None = None
    ) -> Generator[
        tuple[
            tuple[_SubjectType, _PredicateType, _ObjectType],
            Iterator[_ContextType | None],
        ],
        None,
        None,
    ]: ...
    def __len__(self, context: _ContextType | None = None) -> int: ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextIdentifierType, None, None]: ...
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None: ...
    def prefix(self, namespace: URIRef) -> str | None: ...
    def namespace(self, prefix: str) -> URIRef | None: ...
    def namespaces(self) -> Iterator[tuple[str, URIRef]]: ...
    def add_graph(self, graph: Graph) -> None: ...
    def remove_graph(self, graph: Graph) -> None: ...
    def subjects(
        self, predicate: _PredicateType | None = None, object: _ObjectType | None = None
    ) -> Generator[_SubjectType, None, None]: ...
    def predicates(
        self, subject: _SubjectType | None = None, object: _ObjectType | None = None
    ) -> Generator[_PredicateType, None, None]: ...
    def objects(
        self,
        subject: _SubjectType | None = None,
        predicate: _PredicateType | None = None,
    ) -> Generator[_ObjectType, None, None]: ...
    def subject_predicates(
        self, object: _ObjectType | None = None
    ) -> Generator[tuple[_SubjectType, _PredicateType], None, None]: ...
    def subject_objects(
        self, predicate: _PredicateType | None = None
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]: ...
    def predicate_objects(
        self, subject: _SubjectType | None = None
    ) -> Generator[tuple[_PredicateType, _ObjectType], None, None]: ...

class SPARQLUpdateStore(SPARQLStore):
    where_pattern: Incomplete
    STRING_LITERAL1: str
    STRING_LITERAL2: str
    STRING_LITERAL_LONG1: str
    STRING_LITERAL_LONG2: str
    String: Incomplete
    IRIREF: str
    COMMENT: str
    BLOCK_START: str
    BLOCK_END: str
    ESCAPED: str
    BlockContent: Incomplete
    BlockFinding: Incomplete
    BLOCK_FINDING_PATTERN: Incomplete
    postAsEncoded: Incomplete
    autocommit: Incomplete
    dirty_reads: Incomplete
    def __init__(
        self,
        query_endpoint: str | None = None,
        update_endpoint: str | None = None,
        sparql11: bool = True,
        context_aware: bool = True,
        postAsEncoded: bool = True,
        autocommit: bool = True,
        dirty_reads: bool = False,
        **kwds,
    ) -> None: ...
    def query(self, *args: Any, **kwargs: Any) -> Result: ...
    def triples(
        self, *args: Any, **kwargs: Any
    ) -> Iterator[tuple[_TripleType, None]]: ...
    def contexts(
        self, *args: Any, **kwargs: Any
    ) -> Generator[_ContextIdentifierType, None, None]: ...
    def __len__(self, *args: Any, **kwargs: Any) -> int: ...
    query_endpoint: Incomplete
    update_endpoint: Incomplete
    def open(
        self, configuration: str | tuple[str, str], create: bool = False
    ) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def add(
        self,
        spo: _TripleType,
        context: _ContextType | None = None,
        quoted: bool = False,
    ) -> None: ...
    def addN(self, quads: Iterable[_QuadType]) -> None: ...
    def remove(self, spo: _TriplePatternType, context: _ContextType | None) -> None: ...
    def setTimeout(self, timeout) -> None: ...
    debug: Incomplete
    def update(
        self,
        query: Update | str,
        initNs: dict[str, Any] = {},
        initBindings: dict[str, Identifier] = {},
        queryGraph: str | None = None,
        DEBUG: bool = False,
    ): ...
    def add_graph(self, graph: Graph) -> None: ...
    def remove_graph(self, graph: Graph) -> None: ...
    def subjects(
        self, predicate: _PredicateType | None = None, object: _ObjectType | None = None
    ) -> Generator[_SubjectType, None, None]: ...
    def predicates(
        self, subject: _SubjectType | None = None, object: _ObjectType | None = None
    ) -> Generator[_PredicateType, None, None]: ...
    def objects(
        self,
        subject: _SubjectType | None = None,
        predicate: _PredicateType | None = None,
    ) -> Generator[_ObjectType, None, None]: ...
    def subject_predicates(
        self, object: _ObjectType | None = None
    ) -> Generator[tuple[_SubjectType, _PredicateType], None, None]: ...
    def subject_objects(
        self, predicate: _PredicateType | None = None
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]: ...
    def predicate_objects(
        self, subject: _SubjectType | None = None
    ) -> Generator[tuple[_PredicateType, _ObjectType], None, None]: ...
