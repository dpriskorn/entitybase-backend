from _typeshed import Incomplete
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.term import URIRef
from typing import IO, Iterable

__all__ = ["XMLWriter"]

class XMLWriter:
    stream: Incomplete
    element_stack: list[str]
    nm: Incomplete
    extra_ns: Incomplete
    closed: bool
    def __init__(
        self,
        stream: IO[bytes],
        namespace_manager: NamespaceManager,
        encoding: str | None = None,
        decl: int = 1,
        extra_ns: dict[str, Namespace] | None = None,
    ) -> None: ...
    indent: Incomplete
    parent: bool
    def push(self, uri: str) -> None: ...
    def pop(self, uri: str | None = None) -> None: ...
    def element(
        self, uri: str, content: str, attributes: dict[URIRef, str] = {}
    ) -> None: ...
    def namespaces(self, namespaces: Iterable[tuple[str, str]] = None) -> None: ...
    def attribute(self, uri: str, value: str) -> None: ...
    def text(self, text: str) -> None: ...
    def qname(self, uri: str) -> str: ...
