from rdflib.graph import Graph
from rdflib.term import Node

class Resource:
    def __init__(self, graph: Graph, subject: Node) -> None: ...
