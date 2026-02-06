"""RDF triple writers."""

import logging
from typing import Any, TextIO

from models.data.rest_api.v1.entitybase.request.entity.context import StatementWriteContext
from models.rdf_builder.hashing.deduplication_cache import HashDedupeBag
from models.rdf_builder.uri_generator import URIGenerator
from models.rdf_builder.value_formatters import ValueFormatter
from models.rdf_builder.value_node import generate_value_node_uri
from models.rdf_builder.writers.value_node import ValueNodeWriter

logger = logging.getLogger(__name__)


class TripleWriters:
    """Collection of writers for RDF triples in various formats."""

    uri = URIGenerator()

    @staticmethod
    def _needs_value_node(value: Any) -> bool:
        """Check if value requires structured value node."""
        if hasattr(value, "kind"):
            return value.kind in ("time", "quantity", "globe")
        return False

    @staticmethod
    def write_header(output: TextIO) -> None:
        """Write Turtle prefixes to output."""
        from models.rdf_builder.writers.prefixes import TURTLE_PREFIXES

        output.write(TURTLE_PREFIXES)

    @staticmethod
    def write_entity_type(output: TextIO, entity_id: str) -> None:
        """Write entity type triple."""
        output.write(
            f"{TripleWriters.uri.entity_prefixed(entity_id)} a wikibase:Item .\n"
        )

    @staticmethod
    def write_dataset_triples(output: TextIO, entity_id: str) -> None:
        """Write dataset triples for entity."""
        data_uri = TripleWriters.uri.data_prefixed(entity_id)
        entity_uri = TripleWriters.uri.entity_prefixed(entity_id)

        output.write(f"{data_uri} a schema:Dataset .\n")
        output.write(f"{data_uri} schema:about {entity_uri} .\n")
        output.write(
            f"{data_uri} cc:license "
            "<http://creativecommons.org/publicdomain/zero/1.0/> .\n"
        )

    @staticmethod
    def write_label(output: TextIO, entity_id: str, lang: str, label: str) -> None:
        """Write label triple."""
        entity_uri = TripleWriters.uri.entity_prefixed(entity_id)
        output.write(f'{entity_uri} rdfs:label "{label}"@{lang} .\n')

    @staticmethod
    def write_description(
        output: TextIO, entity_id: str, lang: str, description: str
    ) -> None:
        """Write description triple."""
        entity_uri = TripleWriters.uri.entity_prefixed(entity_id)
        output.write(f'{entity_uri} schema:description "{description}"@{lang} .\n')

    @staticmethod
    def write_alias(output: TextIO, entity_id: str, lang: str, alias: str) -> None:
        """Write alias triple."""
        entity_uri = TripleWriters.uri.entity_prefixed(entity_id)
        output.write(f'{entity_uri} skos:altLabel "{alias}"@{lang} .\n')

    @staticmethod
    def write_sitelink(output: TextIO, entity_id: str, sitelink_data: dict) -> None:
        """Write sitelink triple."""
        entity_uri = TripleWriters.uri.entity_prefixed(entity_id)
        site_key = sitelink_data.get("site", "")
        title = sitelink_data.get("title", "")
        wiki_url = f"https://{site_key}.wikipedia.org/wiki/{title.replace(' ', '_')}"
        output.write(f"{entity_uri} schema:sameAs <{wiki_url}> .\n")

    @staticmethod
    def write_redirect(output: TextIO, redirect_id: str, target_id: str) -> None:
        """Write redirect triple: wd:Qredirect owl:sameAs wd:Qtarget."""
        redirect_uri = TripleWriters.uri.entity_prefixed(redirect_id)
        target_uri = TripleWriters.uri.entity_prefixed(target_id)
        output.write(f"{redirect_uri} owl:sameAs {target_uri} .\n")

    @staticmethod
    def write_direct_claim(
        output: TextIO, entity_id: str, property_id: str, value: str
    ) -> None:
        """Write direct claim triple: wd:Qxxx wdt:Pxxx value."""
        entity_uri = TripleWriters.uri.entity_prefixed(entity_id)
        output.write(f"{entity_uri} wdt:{property_id} {value} .\n")

    @staticmethod
    def _write_value_node_triple(
        output: TextIO,
        subject_uri: str,
        predicate_uri: str,
        value: Any,
        dedupe: HashDedupeBag | None = None,
    ) -> None:
        """Write value node triple and node if needed."""
        if TripleWriters._needs_value_node(value):
            node_id = generate_value_node_uri(value)
            output.write(f"{subject_uri} {predicate_uri} wdv:{node_id} .\n")

            if value.kind == "time":
                ValueNodeWriter.write_time_value_node(output, node_id, value, dedupe)
            elif value.kind == "quantity":
                ValueNodeWriter.write_quantity_value_node(output, node_id, value, dedupe)
            elif value.kind == "globe":
                ValueNodeWriter.write_globe_value_node(output, node_id, value, dedupe)

    @staticmethod
    def write_statement(ctx: StatementWriteContext) -> None:
        """Write statement triple."""
        logger.debug(f"Writing statement for entity {ctx.entity_id}, property {ctx.shape.pid}")
        from models.rdf_builder.models.rdf_reference import RDFReference

        entity_uri = TripleWriters.uri.entity_prefixed(ctx.entity_id)
        stmt_uri_prefixed = TripleWriters.uri.statement_prefixed(ctx.rdf_statement.guid)

        # Link entity → statement
        ctx.output.write(
            f"{entity_uri} p:{ctx.rdf_statement.property_id} {stmt_uri_prefixed} .\n"
        )

        if ctx.rdf_statement.rank == "normal":
            ctx.output.write(
                f"{stmt_uri_prefixed} a wikibase:Statement, wikibase:BestRank .\n"
            )

            value = ValueFormatter.format_value(ctx.rdf_statement.value)
            TripleWriters.write_direct_claim(
                ctx.output, ctx.entity_id, ctx.rdf_statement.property_id, value
            )
        else:
            ctx.output.write(f"{stmt_uri_prefixed} a wikibase:Statement .\n")

        # Write statement value
        if TripleWriters._needs_value_node(ctx.rdf_statement.value):
            TripleWriters._write_value_node_triple(
                ctx.output,
                stmt_uri_prefixed,
                ctx.shape.predicates.value_node,
                ctx.rdf_statement.value,
                ctx.dedupe,
            )
        else:
            value = ValueFormatter.format_value(ctx.rdf_statement.value)
            ctx.output.write(
                f"{stmt_uri_prefixed} {ctx.shape.predicates.statement} {value} .\n"
            )

        # Rank
        rank = (
            "NormalRank"
            if ctx.rdf_statement.rank == "normal"
            else (
                "PreferredRank"
                if ctx.rdf_statement.rank == "preferred"
                else "DeprecatedRank"
            )
        )
        ctx.output.write(f"{stmt_uri_prefixed} wikibase:rank wikibase:{rank} .\n")

        # Qualifiers
        for qual in ctx.rdf_statement.qualifiers:
            q_shape = ctx.property_registry.shape(qual.property)

            if TripleWriters._needs_value_node(qual.value):
                TripleWriters._write_value_node_triple(
                    ctx.output,
                    stmt_uri_prefixed,
                    q_shape.predicates.qualifier_value,
                    qual.value,
                    ctx.dedupe,
                )
            else:
                qv = ValueFormatter.format_value(qual.value)
                ctx.output.write(
                    f"{stmt_uri_prefixed} {q_shape.predicates.qualifier} {qv} .\n"
                )

        # References
        for ref in ctx.rdf_statement.references:
            rdf_ref = RDFReference(reference=ref, statement_uri=stmt_uri_prefixed)
            ref_uri = rdf_ref.reference_uri
            ctx.output.write(f"{stmt_uri_prefixed} prov:wasDerivedFrom {ref_uri} .\n")

            for snak in ref.snaks:
                snak_shape = ctx.property_registry.shape(snak.property)

                if TripleWriters._needs_value_node(snak.value):
                    TripleWriters._write_value_node_triple(
                        ctx.output,
                        ref_uri,
                        snak_shape.predicates.reference_value,
                        snak.value,
                        ctx.dedupe,
                    )
                else:
                    rv = ValueFormatter.format_value(snak.value)
                    ctx.output.write(
                        f"{ref_uri} {snak_shape.predicates.reference} {rv} .\n"
                    )
