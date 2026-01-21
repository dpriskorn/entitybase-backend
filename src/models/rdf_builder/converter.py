"""RDF entity converter."""

import logging
from io import StringIO
from pathlib import Path
from typing import Any, TextIO

from pydantic import BaseModel, Field

from models.json_parser.statement_parser import parse_statement
from models.rdf_builder.hashing.deduplication_cache import HashDedupeBag
from models.rdf_builder.models.rdf_statement import RDFStatement
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.redirect_cache import load_entity_redirects
from models.rdf_builder.writers.property_ontology import PropertyOntologyWriter
from models.rdf_builder.writers.triple import TripleWriters
from models.rest_api.entitybase.v1.response.entity import EntityMetadataResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityConverter(BaseModel):
    """Converts internal Entity representation to RDF Turtle format."""
    property_registry: PropertyRegistry
    entity_metadata_dir: Path | None = Field(default=None)
    redirects_dir: Path | None = Field(default=None)
    vitess_client: Any = Field(default=None)
    enable_deduplication: bool = True

    @property
    def properties(self):
        return self.property_registry

    @property
    def writers(self):
        return TripleWriters()

    @property
    def dedupe(self):
        return HashDedupeBag() if self.enable_deduplication else None

    def convert_to_turtle(self, entity: EntityMetadataResponse, output: TextIO) -> None:
        """Convert entity to Turtle format."""
        self.writers.write_header(output)
        self._write_entity_metadata(entity, output)
        self._write_statements(entity, output)
        self._write_redirects(entity, output)
        self._write_referenced_entity_metadata(entity, output)
        self._write_property_metadata(entity, output)

    def _write_entity_metadata(
        self, entity: EntityMetadataResponse, output: TextIO
    ) -> None:
        """Write entity type, labels, descriptions, aliases, sitelinks."""
        self.writers.write_entity_type(output, entity.id)
        self.writers.write_dataset_triples(output, entity.id)

        for lang, label in entity.labels.data.items():
            self.writers.write_label(output, entity.id, lang, label.value)

        for lang, description in entity.descriptions.data.items():
            self.writers.write_description(output, entity.id, lang, description.value)

        for lang, aliases in entity.aliases.data.items():
            for alias in aliases:
                self.writers.write_alias(output, entity.id, lang, alias.value)

        if entity.sitelinks:
            for site_key, sitelink_data in entity.sitelinks.data.items():
                self.writers.write_sitelink(
                    output, entity.id, sitelink_data.model_dump()
                )

    def _write_statements(self, entity: EntityMetadataResponse, output: TextIO) -> None:
        """Write all statements."""
        for stmt_dict in entity.statements.data:
            stmt = parse_statement(stmt_dict)
            rdf_stmt = stmt.get_rdfstatement()
            self._write_statement(entity.id, rdf_stmt, output)

    def _write_statement(
        self, entity_id: str, rdf_stmt: RDFStatement, output: TextIO
    ) -> None:
        """Write single statement with references."""
        shape = self.properties.shape(rdf_stmt.property_id)
        logger.debug(f"Writing statement for {rdf_stmt.property_id}, shape: {shape}")
        self.writers.write_statement(
            output, entity_id, rdf_stmt, shape, self.properties, self.dedupe
        )

    def _write_property_metadata(
        self, entity: EntityMetadataResponse, output: TextIO
    ) -> None:
        """Write property metadata blocks for properties used in entity."""
        property_ids = set()

        # Collect from main statements
        for stmt_dict in entity.statements.data:
            stmt = parse_statement(stmt_dict)
            property_ids.add(stmt.property)

        # Collect from qualifiers and references
        for stmt_dict in entity.statements.data:
            stmt = parse_statement(stmt_dict)
            for qualifier in stmt.qualifiers:
                property_ids.add(qualifier.property)

            for ref in stmt.references:
                for ref_value in ref.snaks:
                    property_ids.add(ref_value.property)

        for pid in sorted(property_ids):
            shape = self.properties.shape(pid)
            PropertyOntologyWriter.write_property_metadata(output, shape)
            PropertyOntologyWriter.write_property(output, shape)
            PropertyOntologyWriter.write_novalue_class(output, pid)

    @staticmethod
    def _collect_referenced_entities(entity: EntityMetadataResponse) -> set[str]:
        """Collect unique entity IDs referenced in statement values, qualifiers, and references."""
        referenced = set()
        for stmt_dict in entity.statements.data:
            stmt = parse_statement(stmt_dict)
            if stmt.value.kind == "entity":
                referenced.add(stmt.value.value)
            for qual in stmt.qualifiers:
                if qual.value.kind == "entity":
                    referenced.add(qual.value.value)
            for ref in stmt.references:
                for ref_value in ref.snaks:
                    if ref_value.value.kind == "entity":
                        referenced.add(ref_value.value.value)
        return referenced

    def _load_referenced_entity(self, entity_id: str) -> EntityMetadataResponse:
        """Load entity metadata (labels, descriptions)."""
        from models.json_parser.entity_parser import parse_entity

        if not self.entity_metadata_dir:
            raise_validation_error(
                f"No entity_metadata_dir set, cannot load {entity_id}",
                exception_class=ValueError,
            )

        assert self.entity_metadata_dir is not None
        json_path = self.entity_metadata_dir / f"{entity_id}.json"
        if json_path.exists():
            import json

            data = json.loads(json_path.read_text(encoding="utf-8"))
            return parse_entity(data)
        raise FileNotFoundError(f"Entity {entity_id} not found at {json_path}")

    def _write_referenced_entity_metadata(
        self, entity: EntityMetadataResponse, output: TextIO
    ) -> None:
        """Write metadata blocks for referenced entities."""
        logger.info(f"Writing referenced entity metadata for entity {entity.id}")
        if not self.entity_metadata_dir:
            return

        referenced_ids = self._collect_referenced_entities(entity)

        for entity_id in sorted(referenced_ids):
            try:
                ref_entity = self._load_referenced_entity(entity_id)
            except Exception:
                logger.warning(
                    f"Metadata file not found for referenced entity {entity_id}"
                )
                continue

            self.writers.write_entity_type(output, ref_entity.id)

            for lang, label in ref_entity.labels.data.items():
                self.writers.write_label(output, ref_entity.id, lang, label.value)

            for lang, description in ref_entity.descriptions.data.items():
                self.writers.write_description(
                    output, ref_entity.id, lang, description.value
                )

    def _fetch_redirects(self, entity_id: str) -> list[str]:
        """Load entity redirects from Vitess or fallback to cache."""
        redirects = []

        if self.vitess_client:
            try:
                vitess_redirects = self.vitess_client.get_incoming_redirects(entity_id)
                redirects.extend(vitess_redirects)
            except Exception as e:
                logger.warning(
                    f"Failed to load redirects from Vitess for {entity_id}: {e}"
                )

        if self.redirects_dir:
            try:
                file_redirects = load_entity_redirects(entity_id, self.redirects_dir)
                redirects.extend(file_redirects)
            except FileNotFoundError:
                logger.debug(f"No redirects found for {entity_id}")

        return list(set(redirects))

    def _write_redirects(self, entity: EntityMetadataResponse, output: TextIO) -> None:
        """Write redirect triples for entity."""
        redirects = self._fetch_redirects(entity.id)
        for redirect_id in redirects:
            self.writers.write_redirect(output, redirect_id, entity.id)

    def convert_to_string(self, entity: EntityMetadataResponse) -> str:
        """Convert entity to Turtle string."""
        buf = StringIO()
        self.convert_to_turtle(entity, buf)
        return buf.getvalue()
