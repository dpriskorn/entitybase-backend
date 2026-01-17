from rdflib.graph import Graph
from rdflib.term import URIRef
from typing import Any, IO

__all__ = ["Serializer"]

class Serializer:
    store: Graph
    encoding: str
    base: str | None
    def __init__(self, store: Graph) -> None: ...
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **args: Any,
    ) -> None: ...
    def relativize(self, uri: _StrT) -> _StrT | URIRef: ...
