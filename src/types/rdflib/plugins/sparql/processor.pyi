from _typeshed import Incomplete
from rdflib.graph import Graph as Graph
from rdflib.plugins.sparql.algebra import (
    translateQuery as translateQuery,
    translateUpdate as translateUpdate,
)
from rdflib.plugins.sparql.evaluate import evalQuery as evalQuery
from rdflib.plugins.sparql.parser import (
    parseQuery as parseQuery,
    parseUpdate as parseUpdate,
)
from rdflib.plugins.sparql.sparql import Query as Query, Update as Update
from rdflib.plugins.sparql.update import evalUpdate as evalUpdate
from rdflib.query import (
    Processor as Processor,
    Result as Result,
    UpdateProcessor as UpdateProcessor,
)
from rdflib.term import Identifier as Identifier
from typing import Any, Mapping

def prepareQuery(
    queryString: str, initNs: Mapping[str, Any] | None = None, base: str | None = None
) -> Query: ...
def prepareUpdate(
    updateString: str, initNs: Mapping[str, Any] | None = None, base: str | None = None
) -> Update: ...
def processUpdate(
    graph: Graph,
    updateString: str,
    initBindings: Mapping[str, Identifier] | None = None,
    initNs: Mapping[str, Any] | None = None,
    base: str | None = None,
) -> None: ...

class SPARQLResult(Result):
    vars: Incomplete
    bindings: Incomplete
    askAnswer: Incomplete
    graph: Incomplete
    def __init__(self, res: Mapping[str, Any]) -> None: ...

class SPARQLUpdateProcessor(UpdateProcessor):
    graph: Incomplete
    def __init__(self, graph) -> None: ...
    def update(
        self,
        strOrQuery: str | Update,
        initBindings: Mapping[str, Identifier] | None = None,
        initNs: Mapping[str, Any] | None = None,
    ) -> None: ...

class SPARQLProcessor(Processor):
    graph: Incomplete
    def __init__(self, graph) -> None: ...
    def query(
        self,
        strOrQuery: str | Query,
        initBindings: Mapping[str, Identifier] | None = None,
        initNs: Mapping[str, Any] | None = None,
        base: str | None = None,
        DEBUG: bool = False,
    ) -> Mapping[str, Any]: ...
