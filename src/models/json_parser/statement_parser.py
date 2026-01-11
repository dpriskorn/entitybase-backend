"""JSON statement parser."""

from typing import Any

from models.json_parser.value_parser import parse_value
from models.json_parser.qualifier_parser import parse_qualifiers
from models.json_parser.reference_parser import parse_references
from models.internal_representation.statements import Statement
from models.internal_representation.ranks import Rank
from models.internal_representation.json_fields import JsonField


def parse_statement(statement_json: dict[str, Any]) -> Statement:
    """Parse statement from Wikidata JSON format."""
    mainsnak = statement_json.get(JsonField.MAINSNAK.value, {})
    rank = Rank(statement_json.get(JsonField.RANK.value, Rank.NORMAL.value))
    qualifiers_json = statement_json.get(JsonField.QUALIFIERS.value, {})
    references_json = statement_json.get(JsonField.REFERENCES.value, [])
    statement_id = statement_json.get(JsonField.STATEMENT_ID.value, "")

    return Statement(
        property=mainsnak.get(JsonField.PROPERTY.value, ""),
        value=parse_value(mainsnak),
        rank=rank,
        qualifiers=parse_qualifiers(qualifiers_json),
        references=parse_references(references_json),
        statement_id=statement_id,
    )
