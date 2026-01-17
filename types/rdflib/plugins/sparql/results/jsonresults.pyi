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
from typing import Any, IO

class JSONResultParser(ResultParser):
    def parse(self, source: IO, content_type: str | None = None) -> Result: ...

class JSONResultSerializer(ResultSerializer):
    def __init__(self, result: Result) -> None: ...
    def serialize(self, stream: IO, encoding: str = None) -> None: ...

class JSONResult(Result):
    json: Incomplete
    askAnswer: Incomplete
    bindings: Incomplete
    vars: Incomplete
    def __init__(self, json: dict[str, Any]) -> None: ...

def parseJsonTerm(d: dict[str, str]) -> Identifier: ...
def termToJSON(self, term: Identifier | None) -> dict[str, str] | None: ...
