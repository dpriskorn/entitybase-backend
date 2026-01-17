from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.serializer import Serializer
from typing import Any, IO

__all__ = ["NQuadsSerializer"]

class NQuadsSerializer(Serializer):
    store: ConjunctiveGraph
    def __init__(self, store: Graph) -> None: ...
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None: ...
