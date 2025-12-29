from typing import TextIO
from io import StringIO
from models.internal_representation.entity import Entity
from .uri_generator import URIGenerator
from .writers.property import PropertyWriter
from .writers.turtle import TurtleWriter
from .writers.triple import TripleWriters
from ..internal_representation.property_metadata import PropertyMetadata


class EntityToRdfConverter:
    """Convert Entity model to RDF Turtle format"""

    def __init__(self, properties: dict[str, PropertyMetadata], base_uri: str = "http://acme.test"):
        self.base_uri = base_uri
        self.properties = properties
        URIGenerator.BASE_URI = base_uri

    def convert_to_turtle(self, entity: Entity, output: TextIO) -> None:
        writer = TurtleWriter(output)
        writer.write_header()

        TripleWriters.write_entity_type(output, entity.id)
        TripleWriters.write_dataset_triples(output, entity.id)

        for prop_id in entity.properties_used():
            PropertyWriter.write_property(output, self.properties[prop_id])

        if entity.labels.items():
            for lang, label in entity.labels.items():
                TripleWriters.write_label(output, entity.id, lang, label)

        if entity.descriptions.items():
            for lang, desc in entity.descriptions.items():
                TripleWriters.write_description(output, entity.id, lang, desc)

        if entity.aliases.items():
            for lang, alias_list in entity.aliases.items():
                for alias in alias_list:
                    TripleWriters.write_alias(output, entity.id, lang, alias)

        if entity.statements:
            for statement in entity.statements:
                TripleWriters.write_statement(output, entity.id, statement)

        if entity.sitelinks:
            for site_key, sitelink_data in entity.sitelinks.items():
                TripleWriters.write_sitelink(output, entity.id, site_key, sitelink_data)

    def convert_to_string(self, entity: Entity) -> str:
        output = StringIO()
        self.convert_to_turtle(entity, output)
        return output.getvalue()
