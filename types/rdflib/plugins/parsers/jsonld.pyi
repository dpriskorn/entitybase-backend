import rdflib.parser
from ..shared.jsonld.context import Context
from _typeshed import Incomplete
from rdflib.graph import Graph
from rdflib.parser import InputSource
from rdflib.term import BNode
from typing import Any

__all__ = ["JsonLDParser", "to_rdf"]

class JsonLDParser(rdflib.parser.Parser):
    def __init__(self) -> None: ...
    def parse(
        self,
        source: InputSource,
        sink: Graph,
        version: float = 1.1,
        skolemize: bool = False,
        encoding: str | None = "utf-8",
        base: str | None = None,
        context: list[dict[str, Any] | str | None] | dict[str, Any] | str | None = None,
        generalized_rdf: bool | None = False,
        extract_all_scripts: bool | None = False,
        **kwargs: Any,
    ) -> None: ...

def to_rdf(
    data: Any,
    dataset: Graph,
    base: str | None = None,
    context_data: list[dict[str, Any] | str | None]
    | dict[str, Any]
    | str
    | None = None,
    version: float | None = None,
    generalized_rdf: bool = False,
    allow_lists_of_lists: bool | None = None,
    skolemize: bool = False,
): ...

class Parser:
    skolemize: Incomplete
    generalized_rdf: Incomplete
    allow_lists_of_lists: Incomplete
    invalid_uri_to_bnode: dict[str, BNode]
    def __init__(
        self,
        generalized_rdf: bool = False,
        allow_lists_of_lists: bool | None = None,
        skolemize: bool = False,
    ) -> None: ...
    def parse(self, data: Any, context: Context, dataset: Graph) -> Graph: ...
