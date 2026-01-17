from ..shared.jsonld.context import Context
from _typeshed import Incomplete
from rdflib.graph import Graph
from rdflib.serializer import Serializer
from rdflib.term import IdentifiedNode, Identifier
from typing import Any, IO

__all__ = ["JsonLDSerializer", "from_rdf"]

class JsonLDSerializer(Serializer):
    def __init__(self, store: Graph) -> None: ...
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None: ...

def from_rdf(
    graph,
    context_data=None,
    base=None,
    use_native_types: bool = False,
    use_rdf_type: bool = False,
    auto_compact: bool = False,
    startnode=None,
    index: bool = False,
): ...

class Converter:
    context: Incomplete
    use_native_types: Incomplete
    use_rdf_type: Incomplete
    def __init__(
        self, context: Context, use_native_types: bool, use_rdf_type: bool
    ) -> None: ...
    def convert(self, graph: Graph): ...
    def from_graph(self, graph: Graph): ...
    def process_subject(self, graph: Graph, s: IdentifiedNode, nodemap): ...
    def add_to_node(
        self,
        graph: Graph,
        s: IdentifiedNode,
        p: IdentifiedNode,
        o: Identifier,
        s_node: dict[str, Any],
        nodemap,
    ): ...
    def type_coerce(self, o: Identifier, coerce_type: str): ...
    def to_raw_value(
        self, graph: Graph, s: IdentifiedNode, o: Identifier, nodemap: dict[str, Any]
    ): ...
    def to_collection(self, graph: Graph, l_: Identifier): ...
