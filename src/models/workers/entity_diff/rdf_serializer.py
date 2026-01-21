from pydantic import BaseModel


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

        # Add entity type
        entity_type = entity_data.get("type", "item")
        if entity_type == "item":
            g.add(
                (entity_uri, RDF.type, URIRef("http://www.wikidata.org/entity/Q35120"))
            )  # item
        elif entity_type == "property":
            g.add(
                (
                    entity_uri,
                    RDF.type,
                    URIRef("http://www.wikidata.org/entity/Q18616576"),
                )
            )  # property

        # Add labels
        labels = entity_data.get("labels", {})
        for lang, label_data in labels.items():
            if isinstance(label_data, dict) and "value" in label_data:
                g.add((entity_uri, RDFS.label, Literal(label_data["value"], lang=lang)))

        # Add descriptions
        descriptions = entity_data.get("descriptions", {})
        for lang, desc_data in descriptions.items():
            if isinstance(desc_data, dict) and "value" in desc_data:
                # Wikibase doesn't have a standard description property in RDF
                # Using schema.org description for now
                g.add(
                    (
                        entity_uri,
                        URIRef("http://schema.org/description"),
                        Literal(desc_data["value"], lang=lang),
                    )
                )

        # Add claims/statements (simplified)
        claims = entity_data.get("claims", {})
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

        return g.serialize(format=format_)  # type: ignore[no-any-return]
