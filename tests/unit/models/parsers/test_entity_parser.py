import json

import pytest

pytestmark = pytest.mark.unit

from models.json_parser import parse_entity

import os
from pathlib import Path

TEST_DATA_JSON_DIR = Path(os.environ["TEST_DATA_DIR"]) / "json"


def test_parse_q3_sitelinks() -> None:
    """Test parsing entity with sitelinks without badges"""
    with open(TEST_DATA_JSON_DIR / "entities/Q3.json") as f:
        entity_json = json.load(f)

    entity = parse_entity(entity_json)
    assert entity.id == "Q3"
    assert entity.type == "item"
    assert entity.sitelinks is not None
    assert "enwiki" in entity.sitelinks.data
    enwiki_sitelink = entity.sitelinks.get("enwiki")
    assert enwiki_sitelink.site == "enwiki"
    assert enwiki_sitelink.title == "San Francisco"
    assert enwiki_sitelink.badges == []
    assert "ruwiki" in entity.sitelinks.data
    ruwiki_sitelink = entity.sitelinks.get("ruwiki")
    assert ruwiki_sitelink.title == "Сан Франциско"


def test_parse_q5_sitelinks_with_badges() -> None:
    """Test parsing entity with sitelinks containing badges"""
    with open(TEST_DATA_JSON_DIR / "entities/Q5.json") as f:
        entity_json = json.load(f)

    entity = parse_entity(entity_json)
    assert entity.id == "Q5"
    assert entity.type == "item"
    assert entity.sitelinks is not None
    assert "enwiki" in entity.sitelinks.data
    enwiki_sitelink = entity.sitelinks.get("enwiki")
    assert enwiki_sitelink.badges == []
    assert "ruwiki" in entity.sitelinks.data
    ruwiki_sitelink = entity.sitelinks.get("ruwiki")
    assert ruwiki_sitelink.badges == ["Q666", "Q42"]


# noinspection PyUnresolvedReferences
def test_parse_q6_complex_qualifiers() -> None:
    """Test parsing entity with complex qualifiers including multiple qualifiers per property"""
    with open(TEST_DATA_JSON_DIR / "entities/Q6.json") as f:
        entity_json = json.load(f)

    entity = parse_entity(entity_json)
    assert entity.id == "Q6"
    assert entity.type == "item"

    p7_statements = [stmt for stmt in entity.statements if stmt.property == "P7"]
    assert len(p7_statements) == 1

    qualifiers = p7_statements[0].qualifiers
    assert len(qualifiers) == 13

    p2_qualifiers = [q for q in qualifiers if q.property == "P2"]
    assert len(p2_qualifiers) == 2
    assert all(q.value.kind == "entity" for q in p2_qualifiers)

    p3_qualifiers = [q for q in qualifiers if q.property == "P3"]
    assert len(p3_qualifiers) == 2

    p5_qualifiers = [q for q in qualifiers if q.property == "P5"]
    assert len(p5_qualifiers) == 3

    p9_qualifiers = [q for q in qualifiers if q.property == "P9"]
    assert len(p9_qualifiers) == 2


def test_parse_entity_with_sitelinks() -> None:
    """Test parsing entity with sitelinks"""
    entity_json = {
        "id": "Q3",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
        "descriptions": {},
        "aliases": {},
        "claims": {},
        "sitelinks": {"enwiki": {"site": "enwiki", "title": "Test", "badges": []}},
    }

    entity = parse_entity(entity_json)
    assert entity.sitelinks is not None
    assert "enwiki" in entity.sitelinks.data
    enwiki_sitelink = entity.sitelinks.get("enwiki")
    assert enwiki_sitelink.site == "enwiki"
