from pathlib import Path
from rdflib.graph import Graph as Graph
from rdflib.namespace import DCTERMS as DCTERMS, OWL as OWL, RDFS as RDFS, SKOS as SKOS
from rdflib.query import ResultRow as ResultRow
from rdflib.util import guess_format as guess_format
from typing import Iterable

def validate_namespace(namespace: str) -> None: ...
def validate_object_id(object_id: str) -> None: ...
def get_target_namespace_elements(
    g: Graph, target_namespace: str
) -> tuple[list[tuple[str, str]], list[str], list[str]]: ...
def make_dn_file(
    output_file_name: Path,
    target_namespace: str,
    elements_strs: Iterable[str],
    non_python_elements_strs: list[str],
    object_id: str,
    fail: bool,
) -> None: ...
