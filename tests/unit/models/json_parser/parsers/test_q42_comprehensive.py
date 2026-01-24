import json
import os
from pathlib import Path

from models.data.infrastructure.s3.enums import EntityType
from models.internal_representation.ranks import Rank
from models.json_parser import parse_entity
from models.data.rest_api.v1.entitybase.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityStatementsResponse,
    EntitySitelinksResponse,
)

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
    assert entity.labels.get("ru").value == "Дуглас Адамс"
    assert entity.labels.get("ja").value == "ダグラス・アダムズ"
    assert entity.labels.get("zh").value == "道格拉斯·亞當斯"
    assert entity.labels.get("ar").value == "دوغلاس آدمز"

    assert isinstance(entity.descriptions, EntityDescriptionsResponse)
    assert len(entity.descriptions.data) == 116
    assert (
        entity.descriptions.get("en").value
        == "British science fiction writer and humorist (1952–2001)"
    )
    assert (
        entity.descriptions.get("fr").value
        == "écrivain de science-fiction et humoriste anglais (1952–2001)"
    )
    assert (
        entity.descriptions.get("de").value
        == "britischer Science-Fiction-Autor und Humorist"
    )
    assert (
        entity.descriptions.get("ru").value
        == "английский писатель, драматург и сценарист и юморист (1952–2001)"
    )

    assert isinstance(entity.aliases, EntityAliasesResponse)
    assert len(entity.aliases.data) == 25
    assert "mul" in entity.aliases.data
    alias_values = entity.aliases.get("mul")
    values = [a.value for a in alias_values]
    assert "Douglas Noël Adams" in values

    assert isinstance(entity.statements, EntityStatementsResponse)
    assert len(entity.statements.data) == 332
    unique_properties = len(set(stmt["property"] for stmt in entity.statements.data))
    assert unique_properties == 293

    p31_statements = [
        stmt for stmt in entity.statements.data if stmt["property"] == "P31"
    ]
    assert len(p31_statements) > 0
    datavalue = p31_statements[0]["mainsnak"]["datavalue"]
    assert datavalue["type"] == "wikibase-entityid"
    assert datavalue["value"]["id"] == "Q5"

    p569_statements = [
        stmt for stmt in entity.statements.data if stmt["property"] == "P569"
    ]
    assert len(p569_statements) > 0
    datavalue = p569_statements[0]["mainsnak"]["datavalue"]
    assert datavalue["type"] == "time"
    assert datavalue["value"]["time"] == "+1952-03-11T00:00:00Z"
    assert datavalue["value"]["precision"] == 11

    p570_statements = [
        stmt for stmt in entity.statements.data if stmt["property"] == "P570"
    ]
    assert len(p570_statements) > 0
    datavalue = p570_statements[0]["mainsnak"]["datavalue"]
    assert datavalue["type"] == "time"
    assert datavalue["value"]["time"] == "+2001-05-11T00:00:00Z"

    p106_statements = [
        stmt for stmt in entity.statements.data if stmt["property"] == "P106"
    ]
    assert len(p106_statements) > 1
    occupation_ids = [
        stmt["mainsnak"]["datavalue"]["value"]["id"]
        for stmt in p106_statements
        if stmt["mainsnak"]["datavalue"]["type"] == "wikibase-entityid"
    ]
    assert len(occupation_ids) > 0

    ranks = [stmt["rank"] for stmt in entity.statements.data]
    assert Rank.NORMAL in ranks
    assert Rank.PREFERRED in ranks

    statements_with_qualifiers = [
        stmt for stmt in entity.statements.data if stmt.get("qualifiers")
    ]
    assert len(statements_with_qualifiers) > 0

    statements_with_references = [
        stmt for stmt in entity.statements.data if stmt.get("references")
    ]
    assert len(statements_with_references) > 0

    assert isinstance(entity.sitelinks, EntitySitelinksResponse)
    assert len(entity.sitelinks.data) == 129
    assert "zhwiki" in entity.sitelinks.data
    assert entity.sitelinks.get("zhwiki").site == "zhwiki"
    assert entity.sitelinks.get("zhwiki").title == "道格拉斯·亚当斯"
    assert entity.sitelinks.get("zhwiki").badges == []
    assert "dewiki" in entity.sitelinks.data
    assert "enwikiquote" in entity.sitelinks.data
    assert "ruwiki" in entity.sitelinks.data
