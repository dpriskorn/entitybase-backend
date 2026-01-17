from _typeshed import Incomplete
from rdflib.graph import Graph
from rdflib.serializer import Serializer
from typing import Any, IO

__all__ = ["TriXSerializer"]

class TriXSerializer(Serializer):
    def __init__(self, store: Graph) -> None: ...
    writer: Incomplete
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None: ...
