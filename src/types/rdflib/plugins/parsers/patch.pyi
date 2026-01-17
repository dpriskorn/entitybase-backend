import typing_extensions as te
from _typeshed import Incomplete
from enum import Enum
from rdflib.graph import Dataset
from rdflib.parser import InputSource
from rdflib.plugins.parsers.nquads import NQuadsParser
from rdflib.term import BNode, URIRef
from typing import Any

__all__ = ["RDFPatchParser", "Operation"]

class Operation(Enum):
    AddTripleOrQuad = "A"
    DeleteTripleOrQuad = "D"
    AddPrefix = "PA"
    DeletePrefix = "PD"
    TransactionStart = "TX"
    TransactionCommit = "TC"
    TransactionAbort = "TA"
    Header = "H"

class RDFPatchParser(NQuadsParser):
    sink: Dataset
    skolemize: Incomplete
    file: Incomplete
    buffer: str
    line: Incomplete
    def parse(
        self,
        inputsource: InputSource,
        sink: Dataset,
        bnode_context: _BNodeContextType | None = None,
        skolemize: bool = False,
        **kwargs: Any,
    ) -> Dataset: ...
    def parsepatch(self, bnode_context: _BNodeContextType | None = None) -> None: ...
    def add_or_remove_triple_or_quad(
        self, operation, bnode_context: _BNodeContextType | None = None
    ) -> None: ...
    def add_prefix(self) -> None: ...
    def delete_prefix(self) -> None: ...
    def operation(self) -> Operation: ...
    def eat_op(self, op: str) -> None: ...
    def nodeid(
        self, bnode_context: _BNodeContextType | None = None
    ) -> te.Literal[False] | BNode | URIRef: ...
    def labeled_bnode(self): ...
