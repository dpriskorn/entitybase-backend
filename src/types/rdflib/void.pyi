from rdflib.graph import Graph as Graph
from rdflib.namespace import RDF as RDF, VOID as VOID
from rdflib.term import (
    IdentifiedNode as IdentifiedNode,
    Literal as Literal,
    URIRef as URIRef,
)

def generateVoID(
    g: Graph,
    dataset: IdentifiedNode | None = None,
    res: Graph | None = None,
    distinctForPartitions: bool = True,
): ...
