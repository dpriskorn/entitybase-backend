import rdflib.namespace
import rdflib.term
from rdflib.graph import Graph
from typing import Any, Callable, Iterable, overload

__all__ = [
    "list2set",
    "first",
    "uniq",
    "more_than",
    "to_term",
    "from_n3",
    "date_time",
    "parse_date_time",
    "guess_format",
    "find_roots",
    "get_tree",
    "_coalesce",
    "_iri2uri",
]

def list2set(seq: Iterable[_HashableT]) -> list[_HashableT]: ...
def first(seq: Iterable[_AnyT]) -> _AnyT | None: ...
def uniq(sequence: Iterable[str], strip: int = 0) -> set[str]: ...
def more_than(sequence: Iterable[Any], number: int) -> int: ...
def to_term(
    s: str | None, default: rdflib.term.Identifier | None = None
) -> rdflib.term.Identifier | None: ...
def from_n3(
    s: str,
    default: str | None = None,
    backend: str | None = None,
    nsm: rdflib.namespace.NamespaceManager | None = None,
) -> rdflib.term.Node | str | None: ...
def date_time(t=None, local_time_zone: bool = False): ...
def parse_date_time(val: str) -> int: ...
def guess_format(fpath: str, fmap: dict[str, str] | None = None) -> str | None: ...
def find_roots(
    graph: Graph, prop: rdflib.term.URIRef, roots: set[rdflib.term.Node] | None = None
) -> set[rdflib.term.Node]: ...
def get_tree(
    graph: Graph,
    root: rdflib.term.Node,
    prop: rdflib.term.URIRef,
    mapper: Callable[[rdflib.term.Node], rdflib.term.Node] = ...,
    sortkey: Callable[[Any], Any] | None = None,
    done: set[rdflib.term.Node] | None = None,
    dir: str = "down",
) -> tuple[rdflib.term.Node, list[Any]] | None: ...
@overload
def _coalesce(*args: _AnyT | None, default: _AnyT) -> _AnyT: ...
@overload
def _coalesce(*args: _AnyT | None, default: _AnyT | None = ...) -> _AnyT | None: ...
def _iri2uri(iri: str) -> str: ...
