from _typeshed import Incomplete
from rdflib.namespace import XSD as XSD
from rdflib.term import URIRef as URIRef

XSD_DTs: set[URIRef]
XSD_DateTime_DTs: Incomplete
XSD_Duration_DTs: Incomplete

def type_promotion(t1: URIRef, t2: URIRef | None) -> URIRef: ...
