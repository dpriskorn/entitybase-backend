from rdflib.graph import Graph
from rdflib.serializer import Serializer
from typing import Any, IO

__all__ = ["NTSerializer"]

class NTSerializer(Serializer):
    def __init__(self, store: Graph) -> None: ...
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = "utf-8",
        **kwargs: Any,
    ) -> None: ...

class NT11Serializer(NTSerializer):
    def __init__(self, store: Graph) -> None: ...
