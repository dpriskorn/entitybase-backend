from _typeshed import Incomplete
from rdflib.graph import Dataset, Graph
from rdflib.parser import InputSource
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser
from typing import Any

__all__ = ["NQuadsParser"]

class NQuadsParser(W3CNTriplesParser):
    sink: Dataset
    skolemize: Incomplete
    file: Incomplete
    buffer: str
    line: Incomplete
    def parse(
        self,
        inputsource: InputSource,
        sink: Graph,
        bnode_context: _BNodeContextType | None = None,
        skolemize: bool = False,
        **kwargs: Any,
    ): ...
    def parseline(self, bnode_context: _BNodeContextType | None = None) -> None: ...
