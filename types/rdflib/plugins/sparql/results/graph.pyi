from rdflib.graph import Graph as Graph
from rdflib.query import Result as Result, ResultParser as ResultParser
from typing import IO

class GraphResultParser(ResultParser):
    def parse(self, source: IO, content_type: str | None) -> Result: ...
