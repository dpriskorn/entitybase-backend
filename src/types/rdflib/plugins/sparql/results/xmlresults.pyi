import xml.etree.ElementTree as xml_etree
from _typeshed import Incomplete
from rdflib.query import (
    Result as Result,
    ResultException as ResultException,
    ResultParser as ResultParser,
    ResultSerializer as ResultSerializer,
)
from rdflib.term import (
    BNode as BNode,
    Identifier as Identifier,
    Literal as Literal,
    URIRef as URIRef,
    Variable as Variable,
)
from typing import Any, IO, Sequence

FOUND_LXML: bool
SPARQL_XML_NAMESPACE: str
RESULTS_NS_ET: Incomplete
log: Incomplete

class XMLResultParser(ResultParser):
    def parse(self, source: IO, content_type: str | None = None) -> Result: ...

class XMLResult(Result):
    bindings: Incomplete
    vars: Incomplete
    askAnswer: Incomplete
    def __init__(self, source: IO, content_type: str | None = None) -> None: ...

def parseTerm(element: xml_etree.Element) -> URIRef | Literal | BNode: ...

class XMLResultSerializer(ResultSerializer):
    def __init__(self, result: Result) -> None: ...
    def serialize(self, stream: IO, encoding: str = "utf-8", **kwargs: Any) -> None: ...

class SPARQLXMLWriter:
    writer: Incomplete
    def __init__(self, output: IO, encoding: str = "utf-8") -> None: ...
    def write_header(self, allvarsL: Sequence[Variable]) -> None: ...
    def write_ask(self, val: bool) -> None: ...
    def write_results_header(self) -> None: ...
    def write_start_result(self) -> None: ...
    def write_end_result(self) -> None: ...
    def write_binding(self, name: Variable, val: Identifier) -> None: ...
    def close(self) -> None: ...
