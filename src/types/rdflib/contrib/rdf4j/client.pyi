import contextlib
import httpx
import types
from _typeshed import Incomplete
from collections.abc import Generator
from dataclasses import dataclass
from rdflib import BNode as BNode
from rdflib.contrib.rdf4j.exceptions import (
    RDF4JUnsupportedProtocolError as RDF4JUnsupportedProtocolError,
    RDFLibParserError as RDFLibParserError,
    RepositoryAlreadyExistsError as RepositoryAlreadyExistsError,
    RepositoryError as RepositoryError,
    RepositoryFormatError as RepositoryFormatError,
    RepositoryNotFoundError as RepositoryNotFoundError,
    RepositoryNotHealthyError as RepositoryNotHealthyError,
    TransactionClosedError as TransactionClosedError,
    TransactionCommitError as TransactionCommitError,
    TransactionPingError as TransactionPingError,
    TransactionRollbackError as TransactionRollbackError,
)
from rdflib.contrib.rdf4j.util import (
    build_context_param as build_context_param,
    build_infer_param as build_infer_param,
    build_sparql_query_accept_header as build_sparql_query_accept_header,
    build_spo_param as build_spo_param,
    rdf_payload_to_stream as rdf_payload_to_stream,
    validate_graph_name as validate_graph_name,
    validate_no_bnodes as validate_no_bnodes,
)
from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID as DATASET_DEFAULT_GRAPH_ID,
    Dataset as Dataset,
    Graph as Graph,
)
from rdflib.query import Result as Result
from rdflib.term import (
    IdentifiedNode as IdentifiedNode,
    Literal as Literal,
    URIRef as URIRef,
)
from typing import Any, BinaryIO, Iterable

SubjectType = URIRef | None
PredicateType = URIRef | None
ObjectType = URIRef | Literal | None

@dataclass(frozen=True)
class NamespaceListingResult:
    prefix: str
    namespace: str

class RDF4JNamespaceManager:
    def __init__(self, identifier: str, http_client: httpx.Client) -> None: ...
    @property
    def http_client(self): ...
    @property
    def identifier(self): ...
    def list(self) -> list[NamespaceListingResult]: ...
    def clear(self) -> None: ...
    def get(self, prefix: str) -> str | None: ...
    def set(self, prefix: str, namespace: str): ...
    def remove(self, prefix: str): ...

class GraphStoreManager:
    def __init__(self, identifier: str, http_client: httpx.Client) -> None: ...
    @property
    def http_client(self): ...
    @property
    def identifier(self): ...
    def get(self, graph_name: URIRef | str) -> Graph: ...
    def add(self, graph_name: URIRef | str, data: str | bytes | BinaryIO | Graph): ...
    def overwrite(
        self, graph_name: URIRef | str, data: str | bytes | BinaryIO | Graph
    ): ...
    def clear(self, graph_name: URIRef | str): ...

@dataclass(frozen=True)
class RepositoryListingResult:
    identifier: str
    uri: str
    readable: bool
    writable: bool
    title: str | None = ...

class Repository:
    def __init__(self, identifier: str, http_client: httpx.Client) -> None: ...
    @property
    def http_client(self): ...
    @property
    def identifier(self): ...
    @property
    def namespaces(self) -> RDF4JNamespaceManager: ...
    @property
    def graphs(self) -> GraphStoreManager: ...
    def health(self) -> bool: ...
    def size(
        self, graph_name: URIRef | Iterable[URIRef] | str | None = None
    ) -> int: ...
    def query(self, query: str, **kwargs): ...
    def update(self, query: str): ...
    def graph_names(self) -> list[IdentifiedNode]: ...
    def get(
        self,
        subj: SubjectType = None,
        pred: PredicateType = None,
        obj: ObjectType = None,
        graph_name: URIRef | Iterable[URIRef] | str | None = None,
        infer: bool = True,
        content_type: str | None = None,
    ) -> Graph | Dataset: ...
    def upload(
        self,
        data: str | bytes | BinaryIO | Graph | Dataset,
        base_uri: str | None = None,
        content_type: str | None = None,
    ): ...
    def overwrite(
        self,
        data: str | bytes | BinaryIO | Graph | Dataset,
        graph_name: URIRef | Iterable[URIRef] | str | None = None,
        base_uri: str | None = None,
        content_type: str | None = None,
    ): ...
    def delete(
        self,
        subj: SubjectType = None,
        pred: PredicateType = None,
        obj: ObjectType = None,
        graph_name: URIRef | Iterable[URIRef] | str | None = None,
    ) -> None: ...
    @contextlib.contextmanager
    def transaction(self) -> Generator[Incomplete]: ...

class Transaction:
    def __init__(self, repo: Repository) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ): ...
    @property
    def repo(self): ...
    @property
    def url(self): ...
    @property
    def is_closed(self) -> bool: ...
    def open(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def ping(self) -> None: ...
    def size(self, graph_name: URIRef | Iterable[URIRef] | str | None = None): ...
    def query(self, query: str, **kwargs): ...
    def update(self, query: str, **kwargs): ...
    def upload(
        self,
        data: str | bytes | BinaryIO | Graph | Dataset,
        base_uri: str | None = None,
        content_type: str | None = None,
    ): ...
    def get(
        self,
        subj: SubjectType = None,
        pred: PredicateType = None,
        obj: ObjectType = None,
        graph_name: URIRef | Iterable[URIRef] | str | None = None,
        infer: bool = True,
        content_type: str | None = None,
    ) -> Graph | Dataset: ...
    def delete(
        self,
        data: str | bytes | BinaryIO | Graph | Dataset,
        base_uri: str | None = None,
        content_type: str | None = None,
    ) -> None: ...

class RepositoryManager:
    def __init__(self, http_client: httpx.Client) -> None: ...
    @property
    def http_client(self): ...
    def list(self) -> list[RepositoryListingResult]: ...
    def get(self, repository_id: str) -> Repository: ...
    def create(
        self, repository_id: str, data: str, content_type: str = "text/turtle"
    ) -> Repository: ...
    def delete(self, repository_id: str) -> None: ...

class RDF4JClient:
    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        **kwargs: Any,
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None: ...
    @property
    def http_client(self): ...
    @property
    def repositories(self) -> RepositoryManager: ...
    @property
    def protocol(self) -> float: ...
    def close(self) -> None: ...
