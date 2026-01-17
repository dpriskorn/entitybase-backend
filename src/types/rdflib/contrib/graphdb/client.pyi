import rdflib.contrib.rdf4j
from rdflib.contrib.rdf4j import RDF4JClient as RDF4JClient
from rdflib.contrib.rdf4j.exceptions import (
    RepositoryNotFoundError as RepositoryNotFoundError,
    RepositoryNotHealthyError as RepositoryNotHealthyError,
)

class Repository(rdflib.contrib.rdf4j.client.Repository):
    def health(self, timeout: int = 5) -> bool: ...

class RepositoryManager(rdflib.contrib.rdf4j.client.RepositoryManager):
    def get(self, repository_id: str) -> Repository: ...

class GraphDBClient(RDF4JClient): ...
