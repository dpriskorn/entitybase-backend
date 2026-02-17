from __future__ import annotations

from typing import TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from rdflib import Graph, URIRef


class RDFSerializer(BaseModel):
    """Serialize Wikibase entity data to RDF formats."""

    @staticmethod
    def entity_data_to_rdf(entity_data: dict, format_: str = "turtle") -> str:
        """Convert Wikibase entity JSON data to RDF."""
        from rdflib import Graph, URIRef, Literal
        from rdflib.namespace import RDF, RDFS

        g = Graph()
        entity_id = entity_data.get("id", "")
        entity_uri = URIRef(f"http://www.wikidata.org/entity/{entity_id}")

        RDFSerializer._add_entity_type(g, entity_uri, entity_data.get("type", "item"))
        RDFSerializer._add_labels(g, entity_uri, entity_data.get("labels", {}))
        RDFSerializer._add_descriptions(
            g, entity_uri, entity_data.get("descriptions", {})
        )
        RDFSerializer._add_statements(g, entity_uri, entity_data.get("claims", {}))

        return g.serialize(format=format_)  # type: ignore[no-any-return]

    @staticmethod
    def _add_entity_type(g: Graph, entity_uri: URIRef, entity_type: str) -> None:
        """Add entity type triple to the graph."""
        from rdflib import URIRef
        from rdflib.namespace import RDF

        if entity_type == "item":
            g.add(
                (entity_uri, RDF.type, URIRef("http://www.wikidata.org/entity/Q35120"))
            )
        elif entity_type == "property":
            g.add(
                (
                    entity_uri,
                    RDF.type,
                    URIRef("http://www.wikidata.org/entity/Q18616576"),
                )
            )

    @staticmethod
    def _add_labels(g: Graph, entity_uri: URIRef, labels: dict) -> None:
        """Add label triples to the graph."""
        from rdflib import Literal
        from rdflib.namespace import RDFS

        for lang, label_data in labels.items():
            if isinstance(label_data, dict) and "value" in label_data:
                g.add((entity_uri, RDFS.label, Literal(label_data["value"], lang=lang)))

    @staticmethod
    def _add_descriptions(g: Graph, entity_uri: URIRef, descriptions: dict) -> None:
        """Add description triples to the graph."""
        from rdflib import Literal, URIRef

        for lang, desc_data in descriptions.items():
            if isinstance(desc_data, dict) and "value" in desc_data:
                g.add(
                    (
                        entity_uri,
                        URIRef("http://schema.org/description"),
                        Literal(desc_data["value"], lang=lang),
                    )
                )

    @staticmethod
    def _add_statements(g: Graph, entity_uri: URIRef, claims: dict) -> None:
        """Add statement/claim triples to the graph (simplified - strings only)."""
        from rdflib import Literal, URIRef

        for prop_id, statements in claims.items():
            if isinstance(statements, list):
                for statement in statements:
                    if isinstance(statement, dict):
                        mainsnak = statement.get("mainsnak", {})
                        if mainsnak.get("snaktype") == "value":
                            datavalue = mainsnak.get("datavalue", {})
                            if datavalue.get("type") == "string":
                                value = datavalue.get("value", "")
                                g.add(
                                    (
                                        entity_uri,
                                        URIRef(
                                            f"http://www.wikidata.org/prop/direct/{prop_id}"
                                        ),
                                        Literal(value),
                                    )
                                )
