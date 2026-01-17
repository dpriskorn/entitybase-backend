from _typeshed import Incomplete
from rdflib.graph import Graph as Graph
from rdflib.namespace import Namespace as Namespace, RDF as RDF
from rdflib.query import Result as Result, ResultParser as ResultParser
from rdflib.term import Node as Node, Variable as Variable
from typing import Any, IO

RS: Incomplete

class RDFResultParser(ResultParser):
    def parse(self, source: IO | Graph, **kwargs: Any) -> Result: ...

class RDFResult(Result):
    vars: Incomplete
    bindings: Incomplete
    askAnswer: Incomplete
    graph: Incomplete
    def __init__(self, source: IO | Graph, **kwargs: Any) -> None: ...
