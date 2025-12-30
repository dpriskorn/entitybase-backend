from typing import TextIO
from io import StringIO

from models.rdf_builder.writers.triple import TripleWriters
from models.rdf_builder.models.rdf_statement import RDFStatement
from models.rdf_builder.models.rdf_reference import RDFReference
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.internal_representation.entity import Entity


class EntityConverter:
    """
    Converts internal Entity representation to RDF Turtle format.
    """

    def __init__(self, property_registry: PropertyRegistry):
        self.properties = property_registry
        self.writers = TripleWriters()

    def convert_to_turtle(self, entity: Entity, output: TextIO):
        """Convert entity to Turtle format."""
        self.writers.write_header(output)
        self._write_entity_metadata(entity, output)
        self._write_statements(entity, output)

    def _write_entity_metadata(self, entity: Entity, output: TextIO):
        """Write entity type, labels, descriptions, aliases, sitelinks."""
        self.writers.write_entity_type(output, entity.id)
        self.writers.write_dataset_triples(output, entity.id)

        for lang, label in entity.labels.items():
            self.writers.write_label(output, entity.id, lang, label)

        for lang, description in entity.descriptions.items():
            self.writers.write_description(output, entity.id, lang, description)

        for lang, aliases in entity.aliases.items():
            for alias in aliases:
                self.writers.write_alias(output, entity.id, lang, alias)

        if entity.sitelinks:
            for site_key, sitelink_data in entity.sitelinks.items():
                self.writers.write_sitelink(output, entity.id, sitelink_data)

    def _write_statements(self, entity: Entity, output: TextIO):
        """Write all statements."""
        for stmt in entity.statements:
            rdf_stmt = RDFStatement(stmt)
            self._write_statement(entity.id, rdf_stmt, output)

    def _write_statement(self, entity_id: str, rdf_stmt: RDFStatement, output: TextIO):
        """Write single statement with references."""
        shape = self.properties.shape(rdf_stmt.property_id)
        self.writers.write_statement(output, entity_id, rdf_stmt, shape)

    def convert_to_string(self, entity: Entity) -> str:
        """Convert entity to Turtle string."""
        buf = StringIO()
        self.convert_to_turtle(entity, buf)
        return buf.getvalue()
