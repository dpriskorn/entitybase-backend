from rdflib.namespace import (
    DefinedNamespace as DefinedNamespace,
    Namespace as Namespace,
)
from rdflib.term import URIRef as URIRef

class WGS(DefinedNamespace):
    SpatialThing: URIRef
    Point: URIRef
    alt: URIRef
    lat: URIRef
    lat_long: URIRef
    location: URIRef
    long: URIRef
