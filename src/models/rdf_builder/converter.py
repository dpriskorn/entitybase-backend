from typing import TextIO
from io import StringIO
from models.internal_representation.entity import Entity
from .uri_generator import URIGenerator
from .writers.turtle import TurtleWriter
from .writers.triple import TripleWriters


class EntityToRdfConverter:
    """Convert Entity model to RDF Turtle format"""

    def __init__(self, base_uri: str = "http://acme.test"):
        self.base_uri = base_uri
        URIGenerator.BASE_URI = base_uri

    @staticmethod
    def convert_to_turtle(entity: Entity, output: TextIO) -> None:
        writer = TurtleWriter(output)
        writer.write_header()

        TripleWriters.write_entity_type(output, entity.id)
        TripleWriters.write_dataset_triples(output, entity.id)

        for lang, label in entity.labels.items():
            TripleWriters.write_label(output, entity.id, lang, label)

        for lang, desc in entity.descriptions.items():
            TripleWriters.write_description(output, entity.id, lang, desc)

        for lang, alias_list in entity.aliases.items():
            for alias in alias_list:
                TripleWriters.write_alias(output, entity.id, lang, alias)

        for statement in entity.statements:
            TripleWriters.write_statement(output, entity.id, statement)

        for site_key, sitelink_data in entity.sitelinks.items():
            TripleWriters.write_sitelink(output, entity.id, site_key, sitelink_data)

    def convert_to_string(self, entity: Entity) -> str:
        output = StringIO()
        self.convert_to_turtle(entity, output)
        return output.getvalue()
