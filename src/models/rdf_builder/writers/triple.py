from typing import TextIO, Any

from models.rdf_builder.uri_generator import URIGenerator
from models.rdf_builder.value_formatters import ValueFormatter


class TripleWriters:
    """Write specific RDF triples for entity components"""

    @staticmethod
    def write_entity_type(output: TextIO, entity_id: str):
        uri = URIGenerator.entity_uri(entity_id)
        output.write(f'<{uri}> a wikibase:Item .\n')

    @staticmethod
    def write_dataset_triples(output: TextIO, entity_id: str):
        data_uri = URIGenerator.data_uri(entity_id)
        entity_uri = URIGenerator.entity_uri(entity_id)

        output.write(f'<{data_uri}> a schema:Dataset .\n')
        output.write(f'<{data_uri}> schema:about <{entity_uri}> .\n')
        output.write(f'<{data_uri}> cc:license <http://creativecommons.org/publicdomain/zero/1.0/> .\n')

    @staticmethod
    def write_label(output: TextIO, entity_id: str, lang: str, label: str):
        uri = URIGenerator.entity_uri(entity_id)
        escaped = ValueFormatter.escape_turtle(label)
        output.write(f'<{uri}> rdfs:label "{escaped}"@{lang} .\n')

    @staticmethod
    def write_description(output: TextIO, entity_id: str, lang: str, desc: str):
        uri = URIGenerator.entity_uri(entity_id)
        escaped = ValueFormatter.escape_turtle(desc)
        output.write(f'<{uri}> schema:description "{escaped}"@{lang} .\n')

    @staticmethod
    def write_alias(output: TextIO, entity_id: str, lang: str, alias: str):
        uri = URIGenerator.entity_uri(entity_id)
        escaped = ValueFormatter.escape_turtle(alias)
        output.write(f'<{uri}> skos:altLabel "{escaped}"@{lang} .\n')

    @staticmethod
    def write_statement(output: TextIO, entity_id: str, statement: Any):
        from models.internal_representation.ranks import Rank

        entity_uri = URIGenerator.entity_uri(entity_id)
        statement_uri = URIGenerator.statement_uri(statement.statement_id)

        output.write(f'<{entity_uri}> p:{statement.property} <{statement_uri}> .\n')
        output.write(f'<{statement_uri}> a wikibase:Statement .\n')

        value_str = ValueFormatter.format_value(statement.value)
        output.write(f'<{statement_uri}> ps:{statement.property} {value_str} .\n')

        rank_value = (
            "NormalRank" if statement.rank == Rank.NORMAL else
            "PreferredRank" if statement.rank == Rank.PREFERRED else
            "DeprecatedRank"
        )
        output.write(f'<{statement_uri}> wikibase:rank wikibase:{rank_value} .\n')

        for qualifier in statement.qualifiers:
            qual_value = ValueFormatter.format_value(qualifier.value)
            output.write(f'<{statement_uri}> pq:{qualifier.property} {qual_value} .\n')

        for idx, reference in enumerate(statement.references):
            ref_uri = URIGenerator.reference_uri(statement_uri, idx)
            output.write(f'<{statement_uri}> prov:wasDerivedFrom <{ref_uri}> .\n')

            for ref_snak in reference.snaks:
                ref_value = ValueFormatter.format_value(ref_snak.value)
                output.write(f'<{ref_uri}> pr:{ref_snak.property} {ref_value} .\n')

    @staticmethod
    def write_sitelink(output: TextIO, entity_id: str, site_key: str, sitelink: dict):
        uri = URIGenerator.entity_uri(entity_id)
        url = sitelink.get('url', '')
        output.write(f'<{uri}> schema:sameAs <{url}> .\n')
