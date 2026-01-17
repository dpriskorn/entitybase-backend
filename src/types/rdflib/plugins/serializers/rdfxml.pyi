from _typeshed import Incomplete
from rdflib.graph import Graph
from rdflib.serializer import Serializer
from rdflib.term import Identifier, URIRef
from typing import Any, IO

__all__ = ["fix", "XMLSerializer", "PrettyXMLSerializer"]

class XMLSerializer(Serializer):
    def __init__(self, store: Graph) -> None: ...
    base: Incomplete
    write: Incomplete
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None: ...
    def subject(self, subject: Identifier, depth: int = 1) -> None: ...
    def predicate(
        self, predicate: Identifier, object: Identifier, depth: int = 1
    ) -> None: ...

def fix(val: str) -> str: ...

class PrettyXMLSerializer(Serializer):
    forceRDFAbout: set[URIRef]
    def __init__(self, store: Graph, max_depth: int = 3) -> None: ...
    base: Incomplete
    max_depth: Incomplete
    nm: Incomplete
    writer: Incomplete
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None: ...
    def subject(self, subject: Identifier, depth: int = 1): ...
    def predicate(
        self, predicate: Identifier, object: Identifier, depth: int = 1
    ) -> None: ...
