from _typeshed import Incomplete
from rdflib.plugins.sparql.parser import (
    BLANK_NODE_LABEL as BLANK_NODE_LABEL,
    BooleanLiteral as BooleanLiteral,
    IRIREF as IRIREF,
    LANGTAG as LANGTAG,
    NumericLiteral as NumericLiteral,
    STRING_LITERAL1 as STRING_LITERAL1,
    STRING_LITERAL2 as STRING_LITERAL2,
    Var as Var,
)
from rdflib.plugins.sparql.parserutils import (
    Comp as Comp,
    CompValue as CompValue,
    Param as Param,
)
from rdflib.query import Result as Result, ResultParser as ResultParser
from rdflib.term import BNode as BNode, Literal as RDFLiteral, URIRef as URIRef
from typing import IO

String = STRING_LITERAL1 | STRING_LITERAL2
RDFLITERAL: Incomplete
NONE_VALUE: Incomplete
EMPTY: Incomplete
TERM = RDFLITERAL | IRIREF | BLANK_NODE_LABEL | NumericLiteral | BooleanLiteral
ROW: Incomplete
HEADER: Incomplete

class TSVResultParser(ResultParser):
    def parse(self, source: IO, content_type: str | None = None) -> Result: ...
    def convertTerm(
        self, t: object | RDFLiteral | BNode | CompValue | URIRef
    ) -> object | BNode | URIRef | RDFLiteral | None: ...
