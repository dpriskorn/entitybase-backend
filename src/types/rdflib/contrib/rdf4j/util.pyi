import typing as t
from rdflib.contrib.rdf4j.client import (
    ObjectType as ObjectType,
    PredicateType as PredicateType,
    SubjectType as SubjectType,
)
from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID as DATASET_DEFAULT_GRAPH_ID,
    Dataset as Dataset,
    Graph as Graph,
)
from rdflib.plugins.sparql.processor import prepareQuery as prepareQuery
from rdflib.term import (
    BNode as BNode,
    IdentifiedNode as IdentifiedNode,
    URIRef as URIRef,
)

def build_context_param(
    params: dict[str, str],
    graph_name: IdentifiedNode | t.Iterable[IdentifiedNode] | str | None = None,
) -> None: ...
def build_spo_param(
    params: dict[str, str],
    subj: SubjectType = None,
    pred: PredicateType = None,
    obj: ObjectType = None,
) -> None: ...
def build_infer_param(params: dict[str, str], infer: bool = True) -> None: ...
def rdf_payload_to_stream(
    data: str | bytes | t.BinaryIO | Graph | Dataset,
) -> tuple[t.BinaryIO, bool]: ...
def build_sparql_query_accept_header(query: str, headers: dict[str, str]): ...
def validate_graph_name(graph_name: URIRef | t.Iterable[URIRef] | str | None): ...
def validate_no_bnodes(
    subj: SubjectType,
    pred: PredicateType,
    obj: ObjectType,
    graph_name: URIRef | t.Iterable[URIRef] | str | None,
) -> None: ...
