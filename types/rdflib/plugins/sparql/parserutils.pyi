from _typeshed import Incomplete
from collections import OrderedDict
from pyparsing import ParseResults, ParserElement as ParserElement, TokenConverter
from rdflib.plugins.sparql.sparql import (
    FrozenBindings as FrozenBindings,
    NotBoundError as NotBoundError,
    SPARQLError as SPARQLError,
)
from rdflib.term import BNode as BNode, Identifier as Identifier, Variable as Variable
from typing import Any, Callable, Mapping

def value(
    ctx: FrozenBindings, val: Any, variables: bool = False, errors: bool = False
) -> Any: ...

class ParamValue:
    isList: Incomplete
    name: Incomplete
    tokenList: Incomplete
    def __init__(
        self, name: str, tokenList: list[Any] | ParseResults, isList: bool
    ) -> None: ...

class Param(TokenConverter):
    isList: Incomplete
    def __init__(self, name: str, expr, isList: bool = False) -> None: ...
    def postParse2(self, tokenList: list[Any] | ParseResults) -> ParamValue: ...

class ParamList(Param):
    def __init__(self, name: str, expr) -> None: ...

class CompValue(OrderedDict):
    name: Incomplete
    def __init__(self, name: str, **values) -> None: ...
    def clone(self) -> CompValue: ...
    def __getitem__(self, a): ...
    def get(self, a, variables: bool = False, errors: bool = False): ...
    def __getattr__(self, a: str) -> Any: ...
    def __setattr__(self, __name: str, /, __value: Any) -> None: ...

class Expr(CompValue):
    def __init__(
        self, name: str, evalfn: Callable[[Any, Any], Any] | None = None, **values
    ) -> None: ...
    ctx: Mapping | FrozenBindings | None
    def eval(self, ctx: Any = {}) -> SPARQLError | Any: ...

class Comp(TokenConverter):
    expr: Incomplete
    evalfn: Callable[[Any, Any], Any] | None
    def __init__(self, name: str, expr: ParserElement) -> None: ...
    def postParse(
        self, instring: str, loc: int, tokenList: ParseResults
    ) -> Expr | CompValue: ...
    def setEvalFn(self, evalfn: Callable[[Any, Any], Any]) -> Comp: ...

def prettify_parsetree(t: ParseResults, indent: str = "", depth: int = 0) -> str: ...
