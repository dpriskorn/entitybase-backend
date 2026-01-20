import json

from pathlib import Path
import os

from models.infrastructure.s3.enums import EntityType
from models.internal_representation.ranks import Rank
from models.internal_representation.value_kinds import ValueKind
from models.json_parser import parse_entity
from models.rest_api.entitybase.v1.response import EntityLabelsResponse, EntityDescriptionsResponse, \
    EntityAliasesResponse
from models.rest_api.entitybase.v1.response.entity import EntityStatementsResponse, EntitySitelinksResponse

TEST_DATA_JSON_DIR = Path(os.environ["TEST_DATA_DIR"]) / "json"


# noinspection PyUnresolvedReferences
def test_parse_q42_comprehensive() -> None:
    """Test comprehensive parsing of Q42.json (Douglas Adams entity)"""
    with open(TEST_DATA_JSON_DIR / "entities/Q42.json") as f:
        data = json.load(f)

    entity_json = data["entities"]["Q42"]
    entity = parse_entity(entity_json)

    assert entity.id == "Q42"
    assert entity.type == EntityType.ITEM

    assert isinstance(entity.labels, EntityLabelsResponse)
    assert len(entity.labels.data) == 72
    assert entity.labels["ru"] == "Дуглас Адамс"
    assert entity.labels["ja"] == "ダグラス・アダムズ"
    assert entity.labels["zh"] == "道格拉斯·亞當斯"
    assert entity.labels["ar"] == "دوغلاس آدمز"

    assert isinstance(entity.descriptions, EntityDescriptionsResponse)
    assert len(entity.descriptions.data) == 116
    assert (
        entity.descriptions["en"]
        == "British science fiction writer and humorist (1952–2001)"
    )
    assert (
        entity.descriptions["fr"]
        == "écrivain de science-fiction et humoriste anglais (1952–2001)"
    )
    assert entity.descriptions["de"] == "britischer Science-Fiction-Autor und Humorist"
    assert (
        entity.descriptions["ru"]
        == "английский писатель, драматург и сценарист и юморист (1952–2001)"
    )

    assert isinstance(entity.aliases, EntityAliasesResponse)
    assert len(entity.aliases.data) == 25
    assert "mul" in entity.aliases
    assert "Douglas Noël Adams" in entity.aliases["mul"]

    assert isinstance(entity.statements, EntityStatementsResponse)
    assert len(entity.statements.data) == 332
    unique_properties = len(set(stmt.property for stmt in entity.statements))
    assert unique_properties == 293

    p31_statements = [stmt for stmt in entity.statements if stmt.property == "P31"]
    assert len(p31_statements) > 0
    assert p31_statements[0].value.kind == ValueKind.ENTITY
    assert p31_statements[0].value.value == "Q5"

    p569_statements = [stmt for stmt in entity.statements if stmt.property == "P569"]
    assert len(p569_statements) > 0
    assert p569_statements[0].value.kind == ValueKind.TIME
    assert p569_statements[0].value.value == "+1952-03-11T00:00:00Z"
    assert p569_statements[0].value.precision == 11

    p570_statements = [stmt for stmt in entity.statements if stmt.property == "P570"]
    assert len(p570_statements) > 0
    assert p570_statements[0].value.kind == ValueKind.TIME
    assert p570_statements[0].value.value == "+2001-05-11T00:00:00Z"

    p106_statements = [stmt for stmt in entity.statements if stmt.property == "P106"]
    assert len(p106_statements) > 1
    occupation_ids = [
        stmt.value.value
        for stmt in p106_statements
        if stmt.value.kind == ValueKind.ENTITY
    ]
    assert len(occupation_ids) > 0

    ranks = [stmt.rank for stmt in entity.statements]
    assert Rank.NORMAL in ranks
    assert Rank.PREFERRED in ranks

    statements_with_qualifiers = [stmt for stmt in entity.statements if stmt.qualifiers]
    assert len(statements_with_qualifiers) > 0

    statements_with_references = [stmt for stmt in entity.statements if stmt.references]
    assert len(statements_with_references) > 0

    assert isinstance(entity.sitelinks, EntitySitelinksResponse)
    assert len(entity.sitelinks.data) == 129
    assert "enwiki" in entity.sitelinks
    assert entity.sitelinks["enwiki"]["site"] == "enwiki"
    assert entity.sitelinks["enwiki"]["title"] == "Douglas Adams"
    assert entity.sitelinks["enwiki"]["badges"] == []
    assert "dewiki" in entity.sitelinks
    assert "enwikiquote" in entity.sitelinks
    assert "ruwiki" in entity.sitelinks
