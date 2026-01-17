import pathlib
import rdflib.query
import rdflib.query as query
import types
from _typeshed import Incomplete
from rdflib._type_checking import _NamespaceSetString
from rdflib.collection import Collection
from rdflib.namespace import NamespaceManager
from rdflib.parser import InputSource
from rdflib.paths import Path
from rdflib.plugins.sparql.sparql import Query, Update
from rdflib.resource import Resource
from rdflib.store import Store
from rdflib.term import BNode, IdentifiedNode, Identifier, Node, URIRef
from typing import (
    Any,
    BinaryIO,
    Callable,
    Generator,
    IO,
    Iterable,
    Mapping,
    NoReturn,
    TextIO,
    TypeVar,
    overload,
)

__all__ = [
    "Graph",
    "ConjunctiveGraph",
    "QuotedGraph",
    "Seq",
    "ModificationException",
    "Dataset",
    "UnSupportedAggregateOperation",
    "ReadOnlyGraphAggregate",
    "BatchAddGraph",
    "_ConjunctiveGraphT",
    "_ContextIdentifierType",
    "_DatasetT",
    "_GraphT",
    "_ObjectType",
    "_OptionalIdentifiedQuadType",
    "_OptionalQuadType",
    "_PredicateType",
    "_QuadPathPatternType",
    "_QuadPatternType",
    "_QuadSelectorType",
    "_QuadType",
    "_SubjectType",
    "_TripleOrOptionalQuadType",
    "_TripleOrTriplePathType",
    "_TripleOrQuadPathPatternType",
    "_TripleOrQuadPatternType",
    "_TripleOrQuadSelectorType",
    "_TriplePathPatternType",
    "_TriplePathType",
    "_TriplePatternType",
    "_TripleSelectorType",
    "_TripleType",
]

_SubjectType = Node
_PredicateType = Node
_ObjectType = Node
_ContextIdentifierType = IdentifiedNode
_TripleType: Incomplete
_QuadType: Incomplete
_OptionalQuadType: Incomplete
_TripleOrOptionalQuadType: Incomplete
_OptionalIdentifiedQuadType: Incomplete
_TriplePatternType: Incomplete
_TriplePathPatternType: Incomplete
_QuadPatternType: Incomplete
_QuadPathPatternType: Incomplete
_TripleOrQuadPatternType: Incomplete
_TripleOrQuadPathPatternType: Incomplete
_TripleSelectorType: Incomplete
_QuadSelectorType: Incomplete
_TripleOrQuadSelectorType: Incomplete
_TriplePathType: Incomplete
_TripleOrTriplePathType: Incomplete
_GraphT = TypeVar("_GraphT", bound="Graph")
_ConjunctiveGraphT = TypeVar("_ConjunctiveGraphT", bound="ConjunctiveGraph")
_DatasetT = TypeVar("_DatasetT", bound="Dataset")

class Graph(Node):
    context_aware: bool
    formula_aware: bool
    default_union: bool
    base: str | None
    def __init__(
        self,
        store: Store | str = "default",
        identifier: _ContextIdentifierType | str | None = None,
        namespace_manager: NamespaceManager | None = None,
        base: str | None = None,
        bind_namespaces: _NamespaceSetString = "rdflib",
    ) -> None: ...
    @property
    def store(self) -> Store: ...
    @property
    def identifier(self) -> _ContextIdentifierType: ...
    @property
    def namespace_manager(self) -> NamespaceManager: ...
    @namespace_manager.setter
    def namespace_manager(self, nm: NamespaceManager) -> None: ...
    def toPython(self) -> _GraphT: ...
    def destroy(self, configuration: str) -> _GraphT: ...
    def commit(self) -> _GraphT: ...
    def rollback(self) -> _GraphT: ...
    def open(
        self, configuration: str | tuple[str, str], create: bool = False
    ) -> int | None: ...
    def close(self, commit_pending_transaction: bool = False) -> None: ...
    def add(self, triple: _TripleType) -> _GraphT: ...
    def addN(self, quads: Iterable[_QuadType]) -> _GraphT: ...
    def remove(self, triple: _TriplePatternType) -> _GraphT: ...
    @overload
    def triples(
        self, triple: _TriplePatternType
    ) -> Generator[_TripleType, None, None]: ...
    @overload
    def triples(
        self, triple: _TriplePathPatternType
    ) -> Generator[_TriplePathType, None, None]: ...
    @overload
    def triples(
        self, triple: _TripleSelectorType
    ) -> Generator[_TripleOrTriplePathType, None, None]: ...
    def __getitem__(self, item): ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Generator[_TripleType, None, None]: ...
    def __contains__(self, triple: _TripleSelectorType) -> bool: ...
    def __hash__(self) -> int: ...
    def __cmp__(self, other) -> int: ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __le__(self, other: Graph) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __ge__(self, other: Graph) -> bool: ...
    def __iadd__(self, other: Iterable[_TripleType]) -> _GraphT: ...
    def __isub__(self, other: Iterable[_TripleType]) -> _GraphT: ...
    def __add__(self, other: Graph) -> Graph: ...
    def __mul__(self, other: Graph) -> Graph: ...
    def __sub__(self, other: Graph) -> Graph: ...
    def __xor__(self, other: Graph) -> Graph: ...
    __or__ = __add__
    __and__ = __mul__
    def set(
        self, triple: tuple[_SubjectType, _PredicateType, _ObjectType]
    ) -> _GraphT: ...
    def subjects(
        self,
        predicate: None | Path | _PredicateType = None,
        object: _ObjectType | list[_ObjectType] | None = None,
        unique: bool = False,
    ) -> Generator[_SubjectType, None, None]: ...
    def predicates(
        self,
        subject: _SubjectType | None = None,
        object: _ObjectType | None = None,
        unique: bool = False,
    ) -> Generator[_PredicateType, None, None]: ...
    def objects(
        self,
        subject: _SubjectType | list[_SubjectType] | None = None,
        predicate: None | Path | _PredicateType = None,
        unique: bool = False,
    ) -> Generator[_ObjectType, None, None]: ...
    def subject_predicates(
        self, object: _ObjectType | None = None, unique: bool = False
    ) -> Generator[tuple[_SubjectType, _PredicateType], None, None]: ...
    def subject_objects(
        self, predicate: None | Path | _PredicateType = None, unique: bool = False
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]: ...
    def predicate_objects(
        self, subject: _SubjectType | None = None, unique: bool = False
    ) -> Generator[tuple[_PredicateType, _ObjectType], None, None]: ...
    def triples_choices(
        self, triple: _TripleChoiceType, context: _ContextType | None = None
    ) -> Generator[_TripleType, None, None]: ...
    @overload
    def value(
        self,
        subject: None = ...,
        predicate: None = ...,
        object: _ObjectType | None = ...,
        default: Node | None = ...,
        any: bool = ...,
    ) -> None: ...
    @overload
    def value(
        self,
        subject: _SubjectType | None = ...,
        predicate: None = ...,
        object: None = ...,
        default: Node | None = ...,
        any: bool = ...,
    ) -> None: ...
    @overload
    def value(
        self,
        subject: None = ...,
        predicate: _PredicateType | None = ...,
        object: None = ...,
        default: Node | None = ...,
        any: bool = ...,
    ) -> None: ...
    @overload
    def value(
        self,
        subject: _SubjectType | None = ...,
        predicate: _PredicateType | None = ...,
        object: _ObjectType | None = ...,
        default: Node | None = ...,
        any: bool = ...,
    ) -> Node | None: ...
    def items(self, list: Node) -> Generator[Node, None, None]: ...
    def transitiveClosure(
        self,
        func: Callable[[_TCArgT, Graph], Iterable[_TCArgT]],
        arg: _TCArgT,
        seen: dict[_TCArgT, int] | None = None,
    ): ...
    def transitive_objects(
        self,
        subject: _SubjectType | None,
        predicate: _PredicateType | None,
        remember: dict[_SubjectType | None, int] | None = None,
    ) -> Generator[_SubjectType | None, None, None]: ...
    def transitive_subjects(
        self,
        predicate: _PredicateType | None,
        object: _ObjectType | None,
        remember: dict[_ObjectType | None, int] | None = None,
    ) -> Generator[_ObjectType | None, None, None]: ...
    def qname(self, uri: str) -> str: ...
    def compute_qname(
        self, uri: str, generate: bool = True
    ) -> tuple[str, URIRef, str]: ...
    def bind(
        self,
        prefix: str | None,
        namespace: Any,
        override: bool = True,
        replace: bool = False,
    ) -> None: ...
    def namespaces(self) -> Generator[tuple[str, URIRef], None, None]: ...
    def absolutize(self, uri: str, defrag: int = 1) -> URIRef: ...
    @overload
    def serialize(
        self,
        destination: None,
        format: str,
        base: str | None,
        encoding: str,
        **args: Any,
    ) -> bytes: ...
    @overload
    def serialize(
        self,
        destination: None = ...,
        format: str = ...,
        base: str | None = ...,
        *,
        encoding: str,
        **args: Any,
    ) -> bytes: ...
    @overload
    def serialize(
        self,
        destination: None = ...,
        format: str = ...,
        base: str | None = ...,
        encoding: None = ...,
        **args: Any,
    ) -> str: ...
    @overload
    def serialize(
        self,
        destination: str | pathlib.PurePath | IO[bytes],
        format: str = ...,
        base: str | None = ...,
        encoding: str | None = ...,
        **args: Any,
    ) -> Graph: ...
    @overload
    def serialize(
        self,
        destination: str | pathlib.PurePath | IO[bytes] | None = ...,
        format: str = ...,
        base: str | None = ...,
        encoding: str | None = ...,
        **args: Any,
    ) -> bytes | str | Graph: ...
    def print(
        self, format: str = "turtle", encoding: str = "utf-8", out: TextIO | None = None
    ) -> None: ...
    def parse(
        self,
        source: IO[bytes]
        | TextIO
        | InputSource
        | str
        | bytes
        | pathlib.PurePath
        | None = None,
        publicID: str | None = None,
        format: str | None = None,
        location: str | None = None,
        file: BinaryIO | TextIO | None = None,
        data: str | bytes | None = None,
        **args: Any,
    ) -> Graph: ...
    def query(
        self,
        query_object: str | Query,
        processor: str | query.Processor = "sparql",
        result: str | type[query.Result] = "sparql",
        initNs: Mapping[str, Any] | None = None,
        initBindings: Mapping[str, Identifier] | None = None,
        use_store_provided: bool = True,
        **kwargs: Any,
    ) -> query.Result: ...
    def update(
        self,
        update_object: Update | str,
        processor: str | rdflib.query.UpdateProcessor = "sparql",
        initNs: Mapping[str, Any] | None = None,
        initBindings: Mapping[str, Identifier] | None = None,
        use_store_provided: bool = True,
        **kwargs: Any,
    ) -> None: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...
    def __reduce__(
        self,
    ) -> tuple[type[Graph], tuple[Store, _ContextIdentifierType]]: ...
    def isomorphic(self, other: Graph) -> bool: ...
    def connected(self) -> bool: ...
    def all_nodes(self) -> set[Node]: ...
    def collection(self, identifier: _SubjectType) -> Collection: ...
    def resource(self, identifier: Node | str) -> Resource: ...
    def skolemize(
        self,
        new_graph: Graph | None = None,
        bnode: BNode | None = None,
        authority: str | None = None,
        basepath: str | None = None,
    ) -> Graph: ...
    def de_skolemize(
        self, new_graph: Graph | None = None, uriref: URIRef | None = None
    ) -> Graph: ...
    def cbd(
        self, resource: _SubjectType, *, target_graph: Graph | None = None
    ) -> Graph: ...

class ConjunctiveGraph(Graph):
    context_aware: bool
    default_union: bool
    def __init__(
        self,
        store: Store | str = "default",
        identifier: IdentifiedNode | str | None = None,
        default_graph_base: str | None = None,
    ) -> None: ...
    @property
    def default_context(self): ...
    @default_context.setter
    def default_context(self, value) -> None: ...
    def __contains__(self, triple_or_quad: _TripleOrQuadSelectorType) -> bool: ...
    def add(self, triple_or_quad: _TripleOrOptionalQuadType) -> _ConjunctiveGraphT: ...
    def addN(self, quads: Iterable[_QuadType]) -> _ConjunctiveGraphT: ...
    def remove(
        self, triple_or_quad: _TripleOrOptionalQuadType
    ) -> _ConjunctiveGraphT: ...
    @overload
    def triples(
        self,
        triple_or_quad: _TripleOrQuadPatternType,
        context: _ContextType | None = ...,
    ) -> Generator[_TripleType, None, None]: ...
    @overload
    def triples(
        self,
        triple_or_quad: _TripleOrQuadPathPatternType,
        context: _ContextType | None = ...,
    ) -> Generator[_TriplePathType, None, None]: ...
    @overload
    def triples(
        self,
        triple_or_quad: _TripleOrQuadSelectorType,
        context: _ContextType | None = ...,
    ) -> Generator[_TripleOrTriplePathType, None, None]: ...
    def quads(
        self, triple_or_quad: _TripleOrQuadPatternType | None = None
    ) -> Generator[_OptionalQuadType, None, None]: ...
    def triples_choices(
        self, triple: _TripleChoiceType, context: _ContextType | None = None
    ) -> Generator[_TripleType, None, None]: ...
    def __len__(self) -> int: ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def get_graph(self, identifier: _ContextIdentifierType) -> Graph | None: ...
    def get_context(
        self,
        identifier: _ContextIdentifierType | str | None,
        quoted: bool = False,
        base: str | None = None,
    ) -> Graph: ...
    def remove_context(self, context: _ContextType) -> None: ...
    def context_id(self, uri: str, context_id: str | None = None) -> URIRef: ...
    def parse(
        self,
        source: IO[bytes]
        | TextIO
        | InputSource
        | str
        | bytes
        | pathlib.PurePath
        | None = None,
        publicID: str | None = None,
        format: str | None = None,
        location: str | None = None,
        file: BinaryIO | TextIO | None = None,
        data: str | bytes | None = None,
        **args: Any,
    ) -> Graph: ...
    def __reduce__(
        self,
    ) -> tuple[type[Graph], tuple[Store, _ContextIdentifierType]]: ...

class Dataset(ConjunctiveGraph):
    default_union: Incomplete
    def __init__(
        self,
        store: Store | str = "default",
        default_union: bool = False,
        default_graph_base: str | None = None,
    ) -> None: ...
    @property
    def default_context(self): ...
    @default_context.setter
    def default_context(self, value) -> None: ...
    @property
    def default_graph(self): ...
    @default_graph.setter
    def default_graph(self, value) -> None: ...
    @property
    def identifier(self): ...
    def __reduce__(self) -> tuple[type[Dataset], tuple[Store, bool]]: ...
    def __iadd__(self, other: Iterable[_QuadType]) -> _DatasetT: ...
    def graph(
        self,
        identifier: _ContextIdentifierType | _ContextType | str | None = None,
        base: str | None = None,
    ) -> Graph: ...
    def parse(
        self,
        source: IO[bytes]
        | TextIO
        | InputSource
        | str
        | bytes
        | pathlib.PurePath
        | None = None,
        publicID: str | None = None,
        format: str | None = None,
        location: str | None = None,
        file: BinaryIO | TextIO | None = None,
        data: str | bytes | None = None,
        **args: Any,
    ) -> Dataset: ...
    def add_graph(
        self, g: _ContextIdentifierType | _ContextType | str | None
    ) -> Graph: ...
    def remove_graph(
        self, g: _ContextIdentifierType | _ContextType | str | None
    ) -> _DatasetT: ...
    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def graphs(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]: ...
    def quads(
        self, quad: _TripleOrQuadPatternType | None = None
    ) -> Generator[_OptionalIdentifiedQuadType, None, None]: ...
    def __iter__(self) -> Generator[_OptionalIdentifiedQuadType, None, None]: ...
    @overload
    def serialize(
        self,
        destination: None,
        format: str,
        base: str | None,
        encoding: str,
        **args: Any,
    ) -> bytes: ...
    @overload
    def serialize(
        self,
        destination: None = ...,
        format: str = ...,
        base: str | None = ...,
        *,
        encoding: str,
        **args: Any,
    ) -> bytes: ...
    @overload
    def serialize(
        self,
        destination: None = ...,
        format: str = ...,
        base: str | None = ...,
        encoding: None = ...,
        **args: Any,
    ) -> str: ...
    @overload
    def serialize(
        self,
        destination: str | pathlib.PurePath | IO[bytes],
        format: str = ...,
        base: str | None = ...,
        encoding: str | None = ...,
        **args: Any,
    ) -> Graph: ...
    @overload
    def serialize(
        self,
        destination: str | pathlib.PurePath | IO[bytes] | None = ...,
        format: str = ...,
        base: str | None = ...,
        encoding: str | None = ...,
        **args: Any,
    ) -> bytes | str | Graph: ...

class QuotedGraph(Graph):
    def __init__(
        self, store: Store | str, identifier: _ContextIdentifierType | str | None
    ) -> None: ...
    def add(self, triple: _TripleType) -> _GraphT: ...
    def addN(self, quads: Iterable[_QuadType]) -> _GraphT: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...
    def __reduce__(
        self,
    ) -> tuple[type[Graph], tuple[Store, _ContextIdentifierType]]: ...

class Seq:
    def __init__(self, graph: Graph, subject: _SubjectType) -> None: ...
    def toPython(self) -> Seq: ...
    def __iter__(self) -> Generator[_ObjectType, None, None]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index) -> _ObjectType: ...

class ModificationException(Exception):
    def __init__(self) -> None: ...

class UnSupportedAggregateOperation(Exception):
    def __init__(self) -> None: ...

class ReadOnlyGraphAggregate(ConjunctiveGraph):
    graphs: Incomplete
    def __init__(self, graphs: list[Graph], store: str | Store = "default") -> None: ...
    def destroy(self, configuration: str) -> NoReturn: ...
    def commit(self) -> NoReturn: ...
    def rollback(self) -> NoReturn: ...
    def open(
        self, configuration: str | tuple[str, str], create: bool = False
    ) -> None: ...
    def close(self) -> None: ...
    def add(self, triple: _TripleOrOptionalQuadType) -> NoReturn: ...
    def addN(self, quads: Iterable[_QuadType]) -> NoReturn: ...
    def remove(self, triple: _TripleOrOptionalQuadType) -> NoReturn: ...
    @overload
    def triples(
        self, triple: _TriplePatternType
    ) -> Generator[_TripleType, None, None]: ...
    @overload
    def triples(
        self, triple: _TriplePathPatternType
    ) -> Generator[_TriplePathType, None, None]: ...
    @overload
    def triples(
        self, triple: _TripleSelectorType
    ) -> Generator[_TripleOrTriplePathType, None, None]: ...
    def __contains__(self, triple_or_quad: _TripleOrQuadSelectorType) -> bool: ...
    def quads(
        self, triple_or_quad: _TripleOrQuadSelectorType
    ) -> Generator[
        tuple[_SubjectType, Path | _PredicateType, _ObjectType, _ContextType],
        None,
        None,
    ]: ...
    def __len__(self) -> int: ...
    def __hash__(self) -> NoReturn: ...
    def __cmp__(self, other) -> int: ...
    def __iadd__(self, other: Iterable[_TripleType]) -> NoReturn: ...
    def __isub__(self, other: Iterable[_TripleType]) -> NoReturn: ...
    def triples_choices(
        self, triple: _TripleChoiceType, context: _ContextType | None = None
    ) -> Generator[_TripleType, None, None]: ...
    def qname(self, uri: str) -> str: ...
    def compute_qname(
        self, uri: str, generate: bool = True
    ) -> tuple[str, URIRef, str]: ...
    def bind(
        self, prefix: str | None, namespace: Any, override: bool = True
    ) -> NoReturn: ...
    def namespaces(self) -> Generator[tuple[str, URIRef], None, None]: ...
    def absolutize(self, uri: str, defrag: int = 1) -> NoReturn: ...
    def parse(
        self,
        source: IO[bytes]
        | TextIO
        | InputSource
        | str
        | bytes
        | pathlib.PurePath
        | None,
        publicID: str | None = None,
        format: str | None = None,
        **args: Any,
    ) -> NoReturn: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> NoReturn: ...
    def __reduce__(self) -> NoReturn: ...

class BatchAddGraph:
    graph: Incomplete
    def __init__(
        self, graph: Graph, batch_size: int = 1000, batch_addn: bool = False
    ) -> None: ...
    batch: list[_QuadType]
    count: int
    def reset(self) -> BatchAddGraph: ...
    def add(self, triple_or_quad: _TripleType | _QuadType) -> BatchAddGraph: ...
    def addN(self, quads: Iterable[_QuadType]) -> BatchAddGraph: ...
    def __enter__(self) -> BatchAddGraph: ...
    def __exit__(self, *exc) -> None: ...
