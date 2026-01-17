from _typeshed import Incomplete
from rdflib._type_checking import _NamespaceSetString
from rdflib.graph import Graph
from rdflib.namespace._BRICK import BRICK as BRICK
from rdflib.namespace._CSVW import CSVW as CSVW
from rdflib.namespace._DC import DC as DC
from rdflib.namespace._DCAM import DCAM as DCAM
from rdflib.namespace._DCAT import DCAT as DCAT
from rdflib.namespace._DCMITYPE import DCMITYPE as DCMITYPE
from rdflib.namespace._DCTERMS import DCTERMS as DCTERMS
from rdflib.namespace._DOAP import DOAP as DOAP
from rdflib.namespace._FOAF import FOAF as FOAF
from rdflib.namespace._GEO import GEO as GEO
from rdflib.namespace._ODRL2 import ODRL2 as ODRL2
from rdflib.namespace._ORG import ORG as ORG
from rdflib.namespace._OWL import OWL as OWL
from rdflib.namespace._PROF import PROF as PROF
from rdflib.namespace._PROV import PROV as PROV
from rdflib.namespace._QB import QB as QB
from rdflib.namespace._RDF import RDF as RDF
from rdflib.namespace._RDFS import RDFS as RDFS
from rdflib.namespace._SDO import SDO as SDO
from rdflib.namespace._SH import SH as SH
from rdflib.namespace._SKOS import SKOS as SKOS
from rdflib.namespace._SOSA import SOSA as SOSA
from rdflib.namespace._SSN import SSN as SSN
from rdflib.namespace._TIME import TIME as TIME
from rdflib.namespace._VANN import VANN as VANN
from rdflib.namespace._VOID import VOID as VOID
from rdflib.namespace._WGS import WGS as WGS
from rdflib.namespace._XSD import XSD as XSD
from rdflib.store import Store
from rdflib.term import URIRef
from typing import Any, Iterable

__all__ = [
    "is_ncname",
    "split_uri",
    "Namespace",
    "ClosedNamespace",
    "DefinedNamespace",
    "NamespaceManager",
    "BRICK",
    "CSVW",
    "DC",
    "DCAM",
    "DCAT",
    "DCMITYPE",
    "DCTERMS",
    "DOAP",
    "FOAF",
    "GEO",
    "ODRL2",
    "ORG",
    "OWL",
    "PROF",
    "PROV",
    "QB",
    "RDF",
    "RDFS",
    "SDO",
    "SH",
    "SKOS",
    "SOSA",
    "SSN",
    "TIME",
    "VANN",
    "VOID",
    "WGS",
    "XSD",
]

class Namespace(str):
    def __new__(cls, value: str | bytes) -> Namespace: ...
    @property
    def title(self) -> URIRef: ...
    def term(self, name: str) -> URIRef: ...
    def __getitem__(self, key: str) -> URIRef: ...
    def __getattr__(self, name: str) -> URIRef: ...
    def __contains__(self, ref: str) -> bool: ...

class URIPattern(str):
    def __new__(cls, value: str | bytes) -> URIPattern: ...
    def __mod__(self, *args, **kwargs) -> URIRef: ...
    def format(self, *args, **kwargs) -> URIRef: ...

class DefinedNamespaceMeta(type):
    def __getitem__(cls, name: str, default=None) -> URIRef: ...
    def __getattr__(cls, name: str): ...
    def __add__(cls, other: str) -> URIRef: ...
    def __contains__(cls, item: str) -> bool: ...
    def __dir__(cls) -> Iterable[str]: ...
    def as_jsonld_context(self, pfx: str) -> dict: ...

class DefinedNamespace(metaclass=DefinedNamespaceMeta):
    def __init__(self) -> None: ...

class ClosedNamespace(Namespace):
    def __new__(cls, uri: str, terms: list[str]): ...
    @property
    def uri(self) -> str: ...
    def term(self, name: str) -> URIRef: ...
    def __getitem__(self, key: str) -> URIRef: ...
    def __getattr__(self, name: str) -> URIRef: ...
    def __dir__(self) -> list[str]: ...
    def __contains__(self, ref: str) -> bool: ...

class NamespaceManager:
    graph: Incomplete
    def __init__(
        self, graph: Graph, bind_namespaces: _NamespaceSetString = "rdflib"
    ) -> None: ...
    def __contains__(self, ref: str) -> bool: ...
    def reset(self) -> None: ...
    @property
    def store(self) -> Store: ...
    def qname(self, uri: str) -> str: ...
    def curie(self, uri: str, generate: bool = True) -> str: ...
    def qname_strict(self, uri: str) -> str: ...
    def normalizeUri(self, rdfTerm: str) -> str: ...
    def compute_qname(
        self, uri: str, generate: bool = True
    ) -> tuple[str, URIRef, str]: ...
    def compute_qname_strict(
        self, uri: str, generate: bool = True
    ) -> tuple[str, str, str]: ...
    def expand_curie(self, curie: str) -> URIRef: ...
    def bind(
        self,
        prefix: str | None,
        namespace: Any,
        override: bool = True,
        replace: bool = False,
    ) -> None: ...
    def namespaces(self) -> Iterable[tuple[str, URIRef]]: ...
    def absolutize(self, uri: str, defrag: int = 1) -> URIRef: ...

def is_ncname(name: str) -> int: ...
def split_uri(uri: str, split_start: list[str] = ...) -> tuple[str, str]: ...
