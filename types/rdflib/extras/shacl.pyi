from rdflib import (
    BNode as BNode,
    Graph as Graph,
    Literal as Literal,
    URIRef as URIRef,
    paths as paths,
)
from rdflib.collection import Collection as Collection
from rdflib.namespace import RDF as RDF, SH as SH
from rdflib.paths import Path as Path
from rdflib.term import IdentifiedNode as IdentifiedNode, Node as Node

class SHACLPathError(Exception): ...

def parse_shacl_path(shapes_graph: Graph, path_identifier: Node) -> URIRef | Path: ...
def build_shacl_path(
    path: URIRef | Path, target_graph: Graph | None = None
) -> tuple[IdentifiedNode, Graph | None]: ...
