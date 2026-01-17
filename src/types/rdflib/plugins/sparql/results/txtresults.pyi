from rdflib.namespace import NamespaceManager as NamespaceManager
from rdflib.query import ResultSerializer as ResultSerializer
from rdflib.term import (
    BNode as BNode,
    Literal as Literal,
    URIRef as URIRef,
    Variable as Variable,
)
from typing import IO

class TXTResultSerializer(ResultSerializer):
    def serialize(
        self,
        stream: IO,
        encoding: str = "utf-8",
        *,
        namespace_manager: NamespaceManager | None = None,
        **kwargs,
    ) -> None: ...
