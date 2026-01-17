import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from collections.abc import Generator
from rdflib._type_checking import _MulPathMod
from rdflib.graph import Graph as Graph, _ObjectType, _PredicateType, _SubjectType
from rdflib.namespace import NamespaceManager as NamespaceManager
from rdflib.term import Node as Node, URIRef as URIRef
from typing import Any, Callable, Iterator

ZeroOrMore: str
OneOrMore: str
ZeroOrOne: str

class Path(ABC, metaclass=abc.ABCMeta):
    __or__: Callable[[Path, URIRef | Path], AlternativePath]
    __invert__: Callable[[Path], InvPath]
    __neg__: Callable[[Path], NegatedPath]
    __truediv__: Callable[[Path, URIRef | Path], SequencePath]
    __mul__: Callable[[Path, str], MulPath]
    @abstractmethod
    def eval(
        self,
        graph: Graph,
        subj: _SubjectType | None = None,
        obj: _ObjectType | None = None,
    ) -> Iterator[tuple[_SubjectType, _ObjectType]]: ...
    @abstractmethod
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    def __lt__(self, other: Any) -> bool: ...
    def __ge__(self, other): ...
    def __gt__(self, other): ...
    def __le__(self, other): ...

class InvPath(Path):
    arg: Incomplete
    def __init__(self, arg: Path | URIRef) -> None: ...
    def eval(
        self,
        graph: Graph,
        subj: _SubjectType | None = None,
        obj: _ObjectType | None = None,
    ) -> Generator[tuple[_ObjectType, _SubjectType], None, None]: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...

class SequencePath(Path):
    args: list[Path | URIRef]
    def __init__(self, *args: Path | URIRef) -> None: ...
    def eval(
        self,
        graph: Graph,
        subj: _SubjectType | None = None,
        obj: _ObjectType | None = None,
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...

class AlternativePath(Path):
    args: list[Path | URIRef]
    def __init__(self, *args: Path | URIRef) -> None: ...
    def eval(
        self,
        graph: Graph,
        subj: _SubjectType | None = None,
        obj: _ObjectType | None = None,
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...

class MulPath(Path):
    path: Incomplete
    mod: Incomplete
    zero: bool
    more: bool
    def __init__(self, path: Path | URIRef, mod: _MulPathMod) -> None: ...
    def eval(
        self,
        graph: Graph,
        subj: _SubjectType | None = None,
        obj: _ObjectType | None = None,
        first: bool = True,
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...

class NegatedPath(Path):
    args: list[URIRef | Path]
    def __init__(self, arg: AlternativePath | InvPath | URIRef) -> None: ...
    def eval(self, graph, subj=None, obj=None) -> Generator[Incomplete]: ...
    def n3(self, namespace_manager: NamespaceManager | None = None) -> str: ...

class PathList(list): ...

def path_alternative(self, other: URIRef | Path): ...
def path_sequence(self, other: URIRef | Path): ...
def evalPath(
    graph: Graph,
    t: tuple[_SubjectType | None, None | Path | _PredicateType, _ObjectType | None],
) -> Iterator[tuple[_SubjectType, _ObjectType]]: ...
def eval_path(
    graph: Graph,
    t: tuple[_SubjectType | None, None | Path | _PredicateType, _ObjectType | None],
) -> Iterator[tuple[_SubjectType, _ObjectType]]: ...
def mul_path(p: URIRef | Path, mul: _MulPathMod) -> MulPath: ...
def inv_path(p: URIRef | Path) -> InvPath: ...
def neg_path(p: URIRef | AlternativePath | InvPath) -> NegatedPath: ...
