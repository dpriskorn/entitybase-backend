import rdflib
import re
from .parserutils import (
    Comp as Comp,
    CompValue as CompValue,
    Param as Param,
    ParamList as ParamList,
)
from _typeshed import Incomplete
from pyparsing import ParseResults
from rdflib.compat import decodeUnicodeEscape as decodeUnicodeEscape
from typing import Any, BinaryIO, TextIO

DEBUG: bool

def neg(literal: rdflib.Literal) -> rdflib.Literal: ...
def setLanguage(terms: tuple[Any, str | None]) -> rdflib.Literal: ...
def setDataType(terms: tuple[Any, str | None]) -> rdflib.Literal: ...
def expandTriples(terms: ParseResults) -> list[Any]: ...
def expandBNodeTriples(terms: ParseResults) -> list[Any]: ...
def expandCollection(terms: ParseResults) -> list[list[Any]]: ...

IRIREF: Incomplete
PN_CHARS_BASE_re: str
PN_CHARS_U_re: Incomplete
PN_CHARS_re: Incomplete
PN_PREFIX: Incomplete
PNAME_NS: Incomplete
PN_LOCAL_ESC_re: str
PERCENT_re: str
PLX_re: Incomplete
PN_LOCAL: Incomplete
PNAME_LN: Incomplete
BLANK_NODE_LABEL: Incomplete
VARNAME: Incomplete
VAR1: Incomplete
VAR2: Incomplete
LANGTAG: Incomplete
INTEGER: Incomplete
EXPONENT_re: str
DECIMAL: Incomplete
DOUBLE: Incomplete
INTEGER_POSITIVE: Incomplete
DECIMAL_POSITIVE: Incomplete
DOUBLE_POSITIVE: Incomplete
INTEGER_NEGATIVE: Incomplete
DECIMAL_NEGATIVE: Incomplete
DOUBLE_NEGATIVE: Incomplete
STRING_LITERAL_LONG1: Incomplete
STRING_LITERAL_LONG2: Incomplete
STRING_LITERAL1: Incomplete
STRING_LITERAL2: Incomplete
NIL: Incomplete
ANON: Incomplete
A: Incomplete
BaseDecl: Incomplete
PrefixDecl: Incomplete
Prologue: Incomplete
Var = VAR1 | VAR2
PrefixedName: Incomplete
iri = IRIREF | PrefixedName
String = STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 | STRING_LITERAL1 | STRING_LITERAL2
RDFLiteral: Incomplete
NumericLiteralPositive = DOUBLE_POSITIVE | DECIMAL_POSITIVE | INTEGER_POSITIVE
NumericLiteralNegative = DOUBLE_NEGATIVE | DECIMAL_NEGATIVE | INTEGER_NEGATIVE
NumericLiteralUnsigned = DOUBLE | DECIMAL | INTEGER
NumericLiteral = (
    NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative
)
BooleanLiteral: Incomplete
BlankNode = BLANK_NODE_LABEL | ANON
GraphTerm = iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL
VarOrTerm = Var | GraphTerm
VarOrIri = Var | iri
GraphRef: Incomplete
GraphRefAll: Incomplete
GraphOrDefault: Incomplete
DataBlockValue: Incomplete
Verb = VarOrIri | A
VerbSimple = Var
Integer = INTEGER
TriplesNode: Incomplete
TriplesNodePath: Incomplete
GraphNode = VarOrTerm | TriplesNode
GraphNodePath = VarOrTerm | TriplesNodePath
PathMod: Incomplete
PathOneInPropertySet: Incomplete
Path: Incomplete
PathNegatedPropertySet: Incomplete
PathPrimary: Incomplete
PathElt: Incomplete
PathEltOrInverse: Incomplete
PathSequence: Incomplete
PathAlternative: Incomplete
VerbPath = Path
ObjectPath = GraphNodePath
ObjectListPath: Incomplete
GroupGraphPattern: Incomplete
Collection: Incomplete
CollectionPath: Incomplete
Object = GraphNode
ObjectList: Incomplete
PropertyListPathNotEmpty: Incomplete
PropertyListPath: Incomplete
PropertyListNotEmpty: Incomplete
PropertyList: Incomplete
BlankNodePropertyList: Incomplete
BlankNodePropertyListPath: Incomplete
TriplesSameSubject: Incomplete
TriplesTemplate: Incomplete
QuadsNotTriples: Incomplete
Quads: Incomplete
QuadPattern: Incomplete
QuadData: Incomplete
TriplesSameSubjectPath: Incomplete
TriplesBlock: Incomplete
MinusGraphPattern: Incomplete
GroupOrUnionGraphPattern: Incomplete
Expression: Incomplete
ExpressionList: Incomplete
RegexExpression: Incomplete
SubstringExpression: Incomplete
StrReplaceExpression: Incomplete
ExistsFunc: Incomplete
NotExistsFunc: Incomplete
Aggregate: Incomplete
BuiltInCall: Incomplete
ArgList: Incomplete
iriOrFunction: Incomplete
FunctionCall: Incomplete
BrackettedExpression: Incomplete
PrimaryExpression = (
    BrackettedExpression
    | BuiltInCall
    | iriOrFunction
    | RDFLiteral
    | NumericLiteral
    | BooleanLiteral
    | Var
)
UnaryExpression: Incomplete
MultiplicativeExpression: Incomplete
AdditiveExpression: Incomplete
NumericExpression = AdditiveExpression
RelationalExpression: Incomplete
ValueLogical = RelationalExpression
ConditionalAndExpression: Incomplete
ConditionalOrExpression: Incomplete
Constraint = BrackettedExpression | BuiltInCall | FunctionCall
Filter: Incomplete
SourceSelector = iri
DefaultGraphClause = SourceSelector
NamedGraphClause: Incomplete
DatasetClause: Incomplete
GroupCondition: Incomplete
GroupClause: Incomplete
Load: Incomplete
Clear: Incomplete
Drop: Incomplete
Create: Incomplete
Add: Incomplete
Move: Incomplete
Copy: Incomplete
InsertData: Incomplete
DeleteData: Incomplete
DeleteWhere: Incomplete
DeleteClause: Incomplete
InsertClause: Incomplete
UsingClause: Incomplete
Modify: Incomplete
Update1 = (
    Load
    | Clear
    | Drop
    | Add
    | Move
    | Copy
    | Create
    | InsertData
    | DeleteData
    | DeleteWhere
    | Modify
)
InlineDataOneVar: Incomplete
InlineDataFull: Incomplete
DataBlock = InlineDataOneVar | InlineDataFull
ValuesClause: Incomplete
ConstructTriples: Incomplete
ConstructTemplate: Incomplete
OptionalGraphPattern: Incomplete
GraphGraphPattern: Incomplete
ServiceGraphPattern: Incomplete
Bind: Incomplete
InlineData: Incomplete
GraphPatternNotTriples = (
    GroupOrUnionGraphPattern
    | OptionalGraphPattern
    | MinusGraphPattern
    | GraphGraphPattern
    | ServiceGraphPattern
    | Filter
    | Bind
    | InlineData
)
GroupGraphPatternSub: Incomplete
HavingCondition = Constraint
HavingClause: Incomplete
OrderCondition: Incomplete
OrderClause: Incomplete
LimitClause: Incomplete
OffsetClause: Incomplete
LimitOffsetClauses: Incomplete
SolutionModifier: Incomplete
SelectClause: Incomplete
WhereClause: Incomplete
SubSelect: Incomplete
SelectQuery: Incomplete
ConstructQuery: Incomplete
AskQuery: Incomplete
DescribeQuery: Incomplete
Update: Incomplete
Query: Incomplete
UpdateUnit: Incomplete
QueryUnit = Query
expandUnicodeEscapes_re: re.Pattern

def expandUnicodeEscapes(q: str) -> str: ...
def parseQuery(q: str | bytes | TextIO | BinaryIO) -> ParseResults: ...
def parseUpdate(q: str | bytes | TextIO | BinaryIO) -> CompValue: ...
