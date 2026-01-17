import typing_extensions as te
from _typeshed import Incomplete
from rdflib.query import Result

__all__ = ["SPARQLConnector", "SPARQLConnectorException"]

class SPARQLConnectorException(Exception): ...

class SPARQLConnector:
    returnFormat: Incomplete
    query_endpoint: Incomplete
    update_endpoint: Incomplete
    kwargs: Incomplete
    def __init__(
        self,
        query_endpoint: str | None = None,
        update_endpoint: str | None = None,
        returnFormat: str | None = "xml",
        method: te.Literal["GET", "POST", "POST_FORM"] = "GET",
        auth: tuple[str, str] | None = None,
        **kwargs,
    ) -> None: ...
    @property
    def method(self) -> str: ...
    @method.setter
    def method(self, method: str) -> None: ...
    def query(
        self,
        query: str,
        default_graph: str | None = None,
        named_graph: str | None = None,
    ) -> Result: ...
    def update(
        self,
        query: str,
        default_graph: str | None = None,
        named_graph: str | None = None,
    ) -> None: ...
    def response_mime_types(self) -> str: ...
