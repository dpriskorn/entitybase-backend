from _typeshed import Incomplete
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.plugins.serializers.turtle import TurtleSerializer
from rdflib.term import Node
from typing import Any, IO

__all__ = ["TrigSerializer"]

class TrigSerializer(TurtleSerializer):
    short_name: str
    indentString: Incomplete
    default_context: Node | None
    contexts: Incomplete
    def __init__(self, store: Graph | ConjunctiveGraph) -> None: ...
    store: Incomplete
    def preprocess(self) -> None: ...
    def reset(self) -> None: ...
    stream: Incomplete
    base: Incomplete
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        spacious: bool | None = None,
        **kwargs: Any,
    ) -> None: ...
