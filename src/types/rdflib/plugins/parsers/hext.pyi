from rdflib.graph import Graph
from rdflib.parser import InputSource, Parser
from typing import Any

__all__ = ["HextuplesParser"]

class HextuplesParser(Parser):
    default_context: Graph | None
    skolemize: bool
    def __init__(self) -> None: ...
    def parse(
        self, source: InputSource, graph: Graph, skolemize: bool = False, **kwargs: Any
    ) -> None: ...
