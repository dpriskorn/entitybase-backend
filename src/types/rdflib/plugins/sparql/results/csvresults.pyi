from rdflib.plugins.sparql.processor import SPARQLResult as SPARQLResult
from rdflib.query import (
    Result as Result,
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
from typing import IO

class CSVResultParser(ResultParser):
    delim: str
    def __init__(self) -> None: ...
    def parse(self, source: IO, content_type: str | None = None) -> Result: ...
    def parseRow(
        self, row: list[str], v: list[Variable]
    ) -> dict[Variable, BNode | URIRef | Literal]: ...
    def convertTerm(self, t: str) -> BNode | URIRef | Literal | None: ...

class CSVResultSerializer(ResultSerializer):
    delim: str
    def __init__(self, result: SPARQLResult) -> None: ...
    def serialize(self, stream: IO, encoding: str = "utf-8", **kwargs) -> None: ...
    def serializeTerm(
        self, term: Identifier | None, encoding: str
    ) -> str | Identifier: ...
