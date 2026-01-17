from _typeshed import Incomplete
from rdflib.graph import (
    ConjunctiveGraph as ConjunctiveGraph,
    Graph as Graph,
    _ContextIdentifierType,
    _ContextType,
    _ObjectType,
    _PredicateType,
    _SubjectType,
    _TriplePatternType,
    _TripleType,
)
from rdflib.query import Result as Result
from rdflib.store import Store as Store
from rdflib.term import URIRef as URIRef
from typing import Any, Generator, Iterator

destructiveOpLocks: Incomplete

class AuditableStore(Store):
    store: Incomplete
    context_aware: Incomplete
    formula_aware: bool
    transaction_aware: bool
    reverseOps: list[
        tuple[
            _SubjectType | None,
            _PredicateType | None,
            _ObjectType | None,
            _ContextIdentifierType | None,
            str,
        ]
    ]
    rollbackLock: Incomplete
    def __init__(self, store: Store) -> None: ...
    def open(
        self, configuration: str | tuple[str, str], create: bool = True
    ) -> int | None: ...
    def close(self, commit_pending_transaction: bool = False) -> None: ...
    def destroy(self, configuration: str) -> None: ...
    def query(self, *args: Any, **kw: Any) -> Result: ...
    def add(
        self, triple: _TripleType, context: _ContextType, quoted: bool = False
    ) -> None: ...
    def remove(
        self, spo: _TriplePatternType, context: _ContextType | None = None
    ) -> None: ...
    def triples(
        self, triple: _TriplePatternType, context: _ContextType | None = None
    ) -> Iterator[tuple[_TripleType, Iterator[_ContextType | None]]]: ...
    def __len__(self, context: _ContextType | None = None): ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None: ...
    def prefix(self, namespace: URIRef) -> str | None: ...
    def namespace(self, prefix: str) -> URIRef | None: ...
    def namespaces(self) -> Iterator[tuple[str, URIRef]]: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
