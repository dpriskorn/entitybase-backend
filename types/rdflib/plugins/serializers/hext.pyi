from rdflib.graph import ConjunctiveGraph, Dataset, Graph
from rdflib.serializer import Serializer
from rdflib.term import IdentifiedNode
from typing import Any, Callable, IO

__all__ = ["HextuplesSerializer"]

class HextuplesSerializer(Serializer):
    contexts: list[Graph | IdentifiedNode]
    dumps: Callable
    def __new__(cls, store: Graph | Dataset | ConjunctiveGraph): ...
    default_context: Graph | IdentifiedNode | None
    graph_type: type[Graph] | type[Dataset] | type[ConjunctiveGraph]
    def __init__(self, store: Graph | Dataset | ConjunctiveGraph) -> None: ...
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = "utf-8",
        **kwargs: Any,
    ) -> None: ...
