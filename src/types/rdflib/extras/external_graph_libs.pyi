from _typeshed import Incomplete
from rdflib.graph import Graph as Graph

logger: Incomplete

def rdflib_to_networkx_multidigraph(graph: Graph, edge_attrs=..., **kwds): ...
def rdflib_to_networkx_digraph(
    graph: Graph, calc_weights: bool = True, edge_attrs=..., **kwds
): ...
def rdflib_to_networkx_graph(
    graph: Graph, calc_weights: bool = True, edge_attrs=..., **kwds
): ...
def rdflib_to_graphtool(
    graph: Graph,
    v_prop_names: list[str] = ["term"],
    e_prop_names: list[str] = ["term"],
    transform_s=...,
    transform_p=...,
    transform_o=...,
): ...
