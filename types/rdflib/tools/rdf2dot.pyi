from _typeshed import Incomplete
from rdflib import XSD as XSD
from rdflib.graph import Graph as Graph
from rdflib.term import Literal as Literal, Node as Node, URIRef as URIRef
from typing import Any, TextIO

LABEL_PROPERTIES: Incomplete
XSDTERMS: Incomplete
EDGECOLOR: str
NODECOLOR: str
ISACOLOR: str

def rdf2dot(g: Graph, stream: TextIO, opts: dict[str, Any] = {}): ...
def main() -> None: ...
